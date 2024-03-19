"""API Views for the platform_plugin_elm_credentials plugin."""

from __future__ import annotations

import io
import zipfile

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from pydantic import ValidationError
from rest_framework import permissions, status
from rest_framework.views import APIView

from platform_plugin_elm_credentials.api.credential_builder import CredentialBuilder
from platform_plugin_elm_credentials.api.serializers import ELMCredentialModel, QueryParamsModel
from platform_plugin_elm_credentials.api.utils import api_error, api_field_errors, pydantic_error_to_response
from platform_plugin_elm_credentials.edxapp_wrapper import (
    BearerAuthenticationAllowInactiveUser,
    CourseInstructorRole,
    CourseStaffRole,
    GeneratedCertificate,
    get_user_by_username_or_email,
    get_user_enrollments,
    modulestore,
)

User = get_user_model()


class ElmCredentialBuilderAPIView(APIView):
    """
    API view for retrieving and generating ELMv3 credentials.

    This class handles the retrieval and generation of ELMv3 credentials for the specified course.
    The credentials include information about the user, the course, and the certificate of completion.

    `Use Cases`:

        * GET: Retrieve ELMv3 credential format in a ZIP file for the specified course ID.

    `Example Requests`:

        * GET platform-plugin-elm-credentials/{course_id}/api/credential-builder

            * Path Parameters:
                * course_id (str): The unique identifier for the course (required).

            * Query Parameters:
                * username (str): The username of the user to generate the credential for (optional).
                    If not provided, credentials for all users in the course will be generated.
                * expires_at (str): The date and time when the credential expires (optional).
                    If not provided, the credential will not expire.
                * to_file (bool): Whether to download the credential as a ZIP file (optional).
                    If not provided, the credential will be returned as a file.

    `Example Response`:

        * GET platform-plugin-elm-credentials/{course_id}/api/credential-builder

            * 400: The supplied course_id key is not valid.

            * 403: The user is not a staff user.

            * 404:
                * The course is not found.
                * The user is not found.
                * The user does not have certificate for the course.

            * 200: Returns a ZIP file containing ELM credentials for the learner(s) in the course.
    """

    authentication_classes = (
        JwtAuthentication,
        BearerAuthenticationAllowInactiveUser,
        SessionAuthenticationAllowInactiveUser,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, course_id: str) -> HttpResponse:
        """
        Handles the GET request to retrieve Elm credentials for the specified course ID.

        Parameters:
            request (Request): The HTTP request object.
            course_id (str): The unique identifier for the course.

        Returns:
            HttpResponse: A JSON file containing ELM credential for the user and course.
                If the course or certificate is not found, appropriate error responses are returned.
        """
        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            return api_field_errors(
                {"course_id": f"The supplied {course_id=} key is not valid."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        course_block = modulestore().get_course(course_key)
        if course_block is None:
            return api_field_errors(
                {"course_id": f"The course with {course_id=} is not found."},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        user_has_access = any(
            [
                request.user.is_staff,
                CourseStaffRole(course_key).has_user(request.user),
                CourseInstructorRole(course_key).has_user(request.user),
            ]
        )

        if not user_has_access:
            return api_error(
                "The user does not have access to generate credentials.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        try:
            query_params = QueryParamsModel(**request.query_params.dict()).model_dump()
        except ValidationError as exc:
            return api_field_errors(
                pydantic_error_to_response(exc.errors()),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        credential_username = query_params.get("username")
        if not credential_username:
            json_data = self.generate_bulk_credentials(
                course_id, course_block, query_params
            )
        else:
            json_data = self.generate_single_credential(
                credential_username, course_id, course_block, query_params
            )

        if isinstance(json_data, HttpResponse):
            return json_data

        if not credential_username or query_params.get("to_file"):
            return self.to_zip(course_id, json_data)

        response = HttpResponse(json_data.values())
        return response

    def generate_single_credential(
        self, username: str, course_id: str, course_block, additional_params: dict
    ) -> dict | HttpResponse:
        """
        Generate ELM credentials for the specified user and course.

        Args:
            username (str): The username of the user to generate the credential for.
            course_id (str): The unique identifier for the course.
            course_block (CourseBlockWithMixins): The course block object.
            additional_params (dict): The additional parameters for the credential.

        Returns:
            str | HttpResponse: The JSON representation of the ELM credential model.
                If the user or certificate is not found, appropriate error responses are returned.
        """
        try:
            user = get_user_by_username_or_email(username)
        except User.DoesNotExist:
            return api_field_errors(
                {"username": f"The username='{username}' does not exist."},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        certificate = GeneratedCertificate.certificate_for_student(user, course_id)

        if not certificate:
            return api_error(
                f"The user {user} does not have certificate for {course_id=}.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return {
            self.credential_name(user, course_id): self.create_credential(
                user, certificate, course_block, additional_params
            )
        }

    def generate_bulk_credentials(
        self, course_id: str, course_block, additional_params: dict
    ) -> dict | HttpResponse:
        """
        Generate ELM credentials for all users in the specified course.

        Args:
            course_id (str): The unique identifier for the course.
            course_block (CourseBlockWithMixins): The course block object.
            additional_params (dict): The additional parameters for the credential.

        Returns:
            list[Tuple[str, str]]: The list of tuples containing the filename and JSON data.
        """
        enrollments = get_user_enrollments(course_id).filter(
            user__is_superuser=False, user__is_staff=False
        )

        credentials = {}
        for enrollment in enrollments:
            user = enrollment.user
            certificate = GeneratedCertificate.certificate_for_student(user, course_id)
            if certificate:
                json_data = self.create_credential(
                    user, certificate, course_block, additional_params
                )
                credentials[self.credential_name(user, course_id)] = json_data

        if not credentials:
            return api_error(
                f"No credentials found for {course_id=}.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return credentials

    @staticmethod
    def create_credential(
        user, certificate, course_block, additional_params: dict
    ) -> str:
        """
        Create an ELM credential model from the specified data.

        Args:
            user (User): The user object.
            certificate (GeneratedCertificate): The certificate object.
            course_block (CourseBlockWithMixins): The course block object.
            additional_params (dict): The additional parameters for the credential.

        Returns:
            str: The JSON representation of the ELM credential model.
        """
        credential_builder = CredentialBuilder(
            course_block, user, certificate, additional_params
        )
        data = ELMCredentialModel(**credential_builder.build())
        return data.model_dump_json(indent=2, by_alias=True, exclude_none=True)

    @staticmethod
    def credential_name(user, course_id: str) -> str:
        """
        Generate a name for the credential file.

        Args:
            user (User): The user object.
            course_id (str): The unique identifier for the course.

        Returns:
            str: The name of the credential file.
        """
        return f"credential-{user}-{course_id}.json"

    @staticmethod
    def to_zip(course_id: str, json_data: dict) -> HttpResponse:
        """
        Create a ZIP file from the specified JSON data.

        Args:
            course_id (str): The unique identifier for the course.
            json_data (dict): The JSON data to be zipped.

        Returns:
            HttpResponse: The HTTP response to download the file.
        """
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for filename, content in json_data.items():
                zipf.writestr(filename, content)

        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response[
            "Content-Disposition"
        ] = f'attachment; filename="credentials-{course_id}.zip"'
        return response
