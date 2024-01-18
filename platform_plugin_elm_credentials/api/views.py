"""API Views for the platform_plugin_elm_credentials plugin."""
from django.http import HttpResponse
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from rest_framework import permissions, status
from rest_framework.views import APIView

from platform_plugin_elm_credentials.api.credential_builder import CredentialBuilder
from platform_plugin_elm_credentials.api.serializers import ELMv3DataModel
from platform_plugin_elm_credentials.api.utils import api_error, api_field_errors
from platform_plugin_elm_credentials.edxapp_wrapper import (
    BearerAuthenticationAllowInactiveUser,
    GeneratedCertificate,
    get_course_overview_or_none,
)


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

    `Example Response`:

        * GET platform-plugin-elm-credentials/{course_id}/api/credential-builder

            * 404:
                * The supplied course_id does not exists.
                * The supplied course_id is not found.
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
                {"course_id": f"The supplied {course_id=} does not exists."},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        course = get_course_overview_or_none(course_key)
        if course is None:
            return api_field_errors(
                {"course_id": f"The supplied {course_id=} is not found."},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        user = request.user
        certificate = GeneratedCertificate.certificate_for_student(user, course_id)

        if not certificate:
            return api_error(
                f"The user {user} does not have certificate for {course_id=}.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        credential_builder = CredentialBuilder(course, user, certificate)
        data = ELMv3DataModel(**credential_builder.build())

        serialized_data = data.model_dump_json(indent=2, by_alias=True)

        response = HttpResponse(serialized_data)
        response["Content-Disposition"] = 'attachment; filename="credential.json"'

        return response