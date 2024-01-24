"""API Views for the platform_plugin_elm_credentials plugin."""
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
    modulestore,
)

User = get_user_model()


class ElmCredentialBuilderAPIView(APIView):
    """
    API view for retrieving and generating ELMv3 credentials.

    This class handles the retrieval and generation of ELMv3 credentials for a specified course
    associated with the provided course ID. The credentials include information about the user,
    the course, and the certificate of completion.

    `Use Cases`:

        * GET: Retrieve ELMv3 credential format in a JSON file for the specified course ID.

    `Example Requests`:

        * GET platform-plugin-elm-credentials/{course_id}/api/credential-builder

            * Path Parameters:
                * course_id (str): The unique identifier for the course (required).

            * Query Parameters:
                * username (str): The username of the user to generate the credential for (required).
                * expires_at (str): The date and time when the credential expires (optional).
                * to_file (bool): Whether to download the credential as a JSON file (optional).

    `Example Response`:

        * GET platform-plugin-elm-credentials/{course_id}/api/credential-builder

            * 400: The supplied course_id key is not valid.

            * 403: The user is not a staff user.

            * 404:
                * The course is not found.
                * The user is not found.
                * The user does not have certificate for the course.

            * 200: Returns a JSON file containing ELM credentials for the user and course.
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
        try:
            credential_user = get_user_by_username_or_email(credential_username)
        except User.DoesNotExist:
            return api_field_errors(
                {"username": f"The username='{credential_username}' does not exists."},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        certificate = GeneratedCertificate.certificate_for_student(
            credential_user, course_id
        )

        if not certificate:
            return api_error(
                f"The user {credential_user} does not have certificate for {course_id=}.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        credential_builder = CredentialBuilder(
            course_block, credential_user, certificate, query_params
        )
        data = ELMCredentialModel(**credential_builder.build())

        serialized_data = data.model_dump_json(
            indent=2, by_alias=True, exclude_none=True
        )

        response = HttpResponse(serialized_data)

        if query_params.get("to_file"):
            filename = f"credential-{credential_username}-{course_id}.json"
            response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response
