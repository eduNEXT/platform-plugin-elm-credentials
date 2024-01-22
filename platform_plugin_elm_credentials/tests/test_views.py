""" Tests for the api views."""
import json
from datetime import datetime
from unittest.mock import Mock, patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from platform_plugin_elm_credentials.api.views import ElmCredentialBuilderAPIView

VIEWS_MODULE_PATH = "platform_plugin_elm_credentials.api.views"


class ElmCredentialBuilderAPIViewTest(APITestCase):
    """Tests for the ElmCredentialBuilderAPIView."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ElmCredentialBuilderAPIView.as_view()
        self.url = reverse("credential-builder-api")
        self.request = self.factory.get(self.url)
        self.user = Mock()
        self.user.email = "john@doe.com"
        self.user.profile.name = "John Doe"
        self.course_id = "course-v1:edX+DemoX+Demo_Course"
        self.org = "edX"
        self.display_name = "Demo Course"
        force_authenticate(self.request, user=self.user)

    @patch(f"{VIEWS_MODULE_PATH}.GeneratedCertificate")
    @patch(f"{VIEWS_MODULE_PATH}.get_course_overview_or_none")
    def test_get_elm_credentials(
        self, get_course_overview_mock: Mock, generated_certificate_mock: Mock
    ):
        """Test GET request for Elm credentials."""
        get_course_overview_mock.return_value = Mock(
            org=self.org, display_name=self.display_name
        )
        generated_certificate_mock.certificate_for_student.return_value = Mock(
            created_date=datetime(2024, 1, 1)
        )

        response = self.view(self.request, course_id=self.course_id)
        response_data = json.loads(response.content)
        credential = response_data["credential"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Content-Disposition", response.headers)
        self.assertEqual(
            response_data["deliveryDetails"]["deliveryAddress"], self.user.email
        )
        self.assertEqual(credential["issuer"]["legalName"]["en"], self.org)
        self.assertEqual(credential["credentialSubject"]["givenName"]["en"], "John")
        self.assertEqual(credential["credentialSubject"]["familyName"]["en"], "Doe")
        self.assertEqual(
            credential["credentialSubject"]["fullName"]["en"],
            "John Doe",
        )

    @patch(f"{VIEWS_MODULE_PATH}.GeneratedCertificate")
    @patch(f"{VIEWS_MODULE_PATH}.get_course_overview_or_none")
    def test_get_elm_credentials_with_to_file_query_param_in_false(
        self, get_course_overview_mock: Mock, generated_certificate_mock: Mock
    ):
        """Test GET request for Elm credentials with to_file query param in False."""
        get_course_overview_mock.return_value = Mock(
            org=self.org, display_name=self.display_name
        )
        generated_certificate_mock.certificate_for_student.return_value = Mock(
            created_date=datetime(2024, 1, 1)
        )

        self.request = self.factory.get(self.url, {"to_file": False})
        force_authenticate(self.request, user=self.user)
        response = self.view(self.request, course_id=self.course_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("Content-Disposition", response.headers)

    def test_get_elm_credentials_not_valid_key(self):
        """Test GET request for Elm credentials with invalid course_id."""
        self.course_id = "course-v1+not-valid+Demo_Course"

        response = self.view(self.request, course_id=self.course_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["field_errors"]["course_id"],
            f"The supplied course_id='{self.course_id}' key is not valid.",
        )

    @patch(f"{VIEWS_MODULE_PATH}.get_course_overview_or_none")
    def test_get_elm_credentials_course_not_found(self, get_course_overview_mock: Mock):
        """Test GET request for Elm credentials with course not found."""
        get_course_overview_mock.return_value = None

        response = self.view(self.request, course_id=self.course_id)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["field_errors"]["course_id"],
            f"The course with course_id='{self.course_id}' is not found.",
        )

    @patch(f"{VIEWS_MODULE_PATH}.GeneratedCertificate")
    @patch(f"{VIEWS_MODULE_PATH}.get_course_overview_or_none")
    def test_get_elm_credentials_certificate_not_found(
        self, get_course_overview_mock: Mock, generated_certificate_mock: Mock
    ):
        """Test GET request for Elm credentials with certificate not found."""
        get_course_overview_mock.return_value = Mock(
            org=self.org, display_name=self.display_name
        )
        generated_certificate_mock.certificate_for_student.return_value = None

        response = self.view(self.request, course_id=self.course_id)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["error"][0],
            f"The user {self.user} does not have certificate for course_id='{self.course_id}'.",
        )

    @patch(f"{VIEWS_MODULE_PATH}.GeneratedCertificate")
    @patch(f"{VIEWS_MODULE_PATH}.get_course_overview_or_none")
    def test_get_elm_credentials_with_invalid_query_params(
        self, get_course_overview_mock: Mock, generated_certificate_mock: Mock
    ):
        """Test GET request for Elm credentials with invalid query params."""
        get_course_overview_mock.return_value = Mock(
            org=self.org, display_name=self.display_name
        )
        generated_certificate_mock.certificate_for_student.return_value = Mock()

        self.request = self.factory.get(
            self.url, {"expired_at": "2025-25-25", "to_file": 100}
        )
        force_authenticate(self.request, user=self.user)
        response = self.view(self.request, course_id=self.course_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expired_at", response.data["field_errors"])
        self.assertIn("to_file", response.data["field_errors"])
