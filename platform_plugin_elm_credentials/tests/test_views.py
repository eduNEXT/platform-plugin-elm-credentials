""" Tests for the api views."""
import json
from datetime import datetime
from unittest.mock import Mock, patch

from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from platform_plugin_elm_credentials.api.views import ElmCredentialBuilderAPIView

VIEWS_MODULE_PATH = "platform_plugin_elm_credentials.api.views"


class ElmCredentialBuilderAPIViewTest(APITestCase):
    """Tests for the ElmCredentialBuilderAPIView."""

    modulestore_patch = patch(f"{VIEWS_MODULE_PATH}.modulestore")
    course_staff_role_patch = patch(f"{VIEWS_MODULE_PATH}.CourseStaffRole")
    course_instructor_role_patch = patch(f"{VIEWS_MODULE_PATH}.CourseInstructorRole")
    generated_certificate_patch = patch(f"{VIEWS_MODULE_PATH}.GeneratedCertificate")
    get_user_by_username_or_email_patch = patch(
        f"{VIEWS_MODULE_PATH}.get_user_by_username_or_email"
    )

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ElmCredentialBuilderAPIView.as_view()
        self.url = reverse("credential-builder-api")
        self.request = self.factory.get(self.url, {"username": "john_doe"})
        self.request_user = Mock()
        self.request_user.is_staff = True
        self.credential_user = Mock()
        self.credential_user.email = "john@doe.com"
        self.credential_user.profile.name = "John Doe"
        self.course_id = "course-v1:edX+DemoX+Demo_Course"
        self.org = "edX"
        self.display_name = "Demo Course"
        self.other_course_settings = {
            "ELM_CREDENTIALS_DEFAULTS": {
                "primary_language_code": "POR",
                "primary_language_map": {"fr": "FRA", "de": "DEU"},
                "org_country_code": "PRT",
            }
        }
        self.get_course = Mock(
            org=self.org,
            display_name=self.display_name,
            other_course_settings=self.other_course_settings,
        )
        force_authenticate(self.request, user=self.request_user)

    @generated_certificate_patch
    @get_user_by_username_or_email_patch
    @course_instructor_role_patch
    @course_staff_role_patch
    @modulestore_patch
    def test_get_elm_credentials_with_course_settings(
        self,
        modulestore_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
        get_user_by_username_or_email_mock: Mock,
        generated_certificate_mock: Mock,
    ):
        """Test GET request for Elm credentials."""
        modulestore_mock.return_value.get_course.return_value = self.get_course
        course_staff_role_mock.has_user.return_value = True
        course_instructor_role_mock.has_user.return_value = True
        get_user_by_username_or_email_mock.return_value = self.credential_user
        generated_certificate_mock.certificate_for_student.return_value = Mock(
            created_date=datetime(2024, 1, 1)
        )

        response = self.view(self.request, course_id=self.course_id)
        response_data = json.loads(response.content)
        credential = response_data["credential"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Content-Disposition", response.headers)
        self.assertEqual(
            response_data["deliveryDetails"]["deliveryAddress"],
            self.credential_user.email,
        )
        self.assertEqual(credential["issuer"]["legalName"]["en"], self.org)
        self.assertEqual(credential["credentialSubject"]["givenName"]["en"], "John")
        self.assertEqual(credential["credentialSubject"]["familyName"]["en"], "Doe")
        self.assertEqual(
            credential["credentialSubject"]["fullName"]["en"],
            "John Doe",
        )
        self.assertEqual(
            credential["credentialSubject"]["hasClaim"]["awardedBy"]["awardingBody"][
                "location"
            ]["address"]["countryCode"]["id"].split("/")[-1],
            self.other_course_settings["ELM_CREDENTIALS_DEFAULTS"]["org_country_code"],
        )
        self.assertEqual(
            credential["displayParameter"]["primaryLanguage"]["id"].split("/")[-1],
            self.other_course_settings["ELM_CREDENTIALS_DEFAULTS"][
                "primary_language_code"
            ],
        )

    @generated_certificate_patch
    @get_user_by_username_or_email_patch
    @course_instructor_role_patch
    @course_staff_role_patch
    @modulestore_patch
    def test_get_elm_credentials_with_django_settings(
        self,
        modulestore_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
        get_user_by_username_or_email_mock: Mock,
        generated_certificate_mock: Mock,
    ):
        """Test GET request for Elm credentials."""
        self.get_course.other_course_settings = {}
        modulestore_mock.return_value.get_course.return_value = self.get_course
        course_staff_role_mock.has_user.return_value = True
        course_instructor_role_mock.has_user.return_value = True
        get_user_by_username_or_email_mock.return_value = self.credential_user
        generated_certificate_mock.certificate_for_student.return_value = Mock(
            created_date=datetime(2024, 1, 1)
        )

        response = self.view(self.request, course_id=self.course_id)
        response_data = json.loads(response.content)
        credential = response_data["credential"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Content-Disposition", response.headers)
        self.assertEqual(
            response_data["deliveryDetails"]["deliveryAddress"],
            self.credential_user.email,
        )
        self.assertEqual(credential["issuer"]["legalName"]["en"], self.org)
        self.assertEqual(credential["credentialSubject"]["givenName"]["en"], "John")
        self.assertEqual(credential["credentialSubject"]["familyName"]["en"], "Doe")
        self.assertEqual(
            credential["credentialSubject"]["fullName"]["en"],
            "John Doe",
        )
        self.assertEqual(
            credential["credentialSubject"]["hasClaim"]["awardedBy"]["awardingBody"][
                "location"
            ]["address"]["countryCode"]["id"].split("/")[-1],
            settings.ELM_CREDENTIALS_DEFAULTS.get("org_country_code"),
        )
        self.assertEqual(
            credential["displayParameter"]["primaryLanguage"]["id"].split("/")[-1],
            settings.ELM_CREDENTIALS_DEFAULTS.get("primary_language_code"),
        )

    @override_settings(ELM_CREDENTIALS_DEFAULTS={})
    @generated_certificate_patch
    @get_user_by_username_or_email_patch
    @course_instructor_role_patch
    @course_staff_role_patch
    @modulestore_patch
    def test_get_elm_credentials_with_default_settings(
        self,
        modulestore_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
        get_user_by_username_or_email_mock: Mock,
        generated_certificate_mock: Mock,
    ):
        """Test GET request for Elm credentials."""
        self.get_course.other_course_settings = {}
        modulestore_mock.return_value.get_course.return_value = self.get_course
        course_staff_role_mock.has_user.return_value = True
        course_instructor_role_mock.has_user.return_value = True
        get_user_by_username_or_email_mock.return_value = self.credential_user
        generated_certificate_mock.certificate_for_student.return_value = Mock(
            created_date=datetime(2024, 1, 1)
        )

        response = self.view(self.request, course_id=self.course_id)
        response_data = json.loads(response.content)
        credential = response_data["credential"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Content-Disposition", response.headers)
        self.assertEqual(
            response_data["deliveryDetails"]["deliveryAddress"],
            self.credential_user.email,
        )
        self.assertEqual(credential["issuer"]["legalName"]["en"], self.org)
        self.assertEqual(credential["credentialSubject"]["givenName"]["en"], "John")
        self.assertEqual(credential["credentialSubject"]["familyName"]["en"], "Doe")
        self.assertEqual(
            credential["credentialSubject"]["fullName"]["en"],
            "John Doe",
        )
        self.assertEqual(
            credential["credentialSubject"]["hasClaim"]["awardedBy"]["awardingBody"][
                "location"
            ]["address"]["countryCode"]["id"].split("/")[-1],
            "ESP",
        )
        self.assertEqual(
            credential["displayParameter"]["primaryLanguage"]["id"].split("/")[-1],
            "SPA",
        )

    @generated_certificate_patch
    @get_user_by_username_or_email_patch
    @course_instructor_role_patch
    @course_staff_role_patch
    @modulestore_patch
    def test_get_elm_credentials_with_to_file_query_param_in_false(
        self,
        modulestore_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
        get_user_by_username_or_email_mock: Mock,
        generated_certificate_mock: Mock,
    ):
        """Test GET request for Elm credentials with to_file query param in False."""
        modulestore_mock.return_value.get_course.return_value = self.get_course
        course_staff_role_mock.has_user.return_value = True
        course_instructor_role_mock.has_user.return_value = True
        get_user_by_username_or_email_mock.return_value = self.credential_user
        generated_certificate_mock.certificate_for_student.return_value = Mock(
            created_date=datetime(2024, 1, 1)
        )

        self.request = self.factory.get(
            self.url, {"username": "john_doe", "to_file": False}
        )
        force_authenticate(self.request, user=self.request_user)
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

    @modulestore_patch
    def test_get_elm_credentials_course_not_found(self, modulestore_mock: Mock):
        """Test GET request for Elm credentials with course not found."""
        modulestore_mock.return_value.get_course.return_value = None
        response = self.view(self.request, course_id=self.course_id)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["field_errors"]["course_id"],
            f"The course with course_id='{self.course_id}' is not found.",
        )

    @generated_certificate_patch
    @get_user_by_username_or_email_patch
    @course_instructor_role_patch
    @course_staff_role_patch
    @modulestore_patch
    def test_get_elm_credentials_certificate_not_found(
        self,
        modulestore_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
        get_user_by_username_or_email_mock: Mock,
        generated_certificate_mock: Mock,
    ):
        """Test GET request for Elm credentials with certificate not found."""
        modulestore_mock.return_value.get_course.return_value = self.get_course
        course_staff_role_mock.has_user.return_value = True
        course_instructor_role_mock.has_user.return_value = True
        get_user_by_username_or_email_mock.return_value = self.credential_user
        generated_certificate_mock.certificate_for_student.return_value = None

        response = self.view(self.request, course_id=self.course_id)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["error"][0],
            f"The user {self.credential_user} does not have certificate for course_id='{self.course_id}'.",
        )

    @course_instructor_role_patch
    @course_staff_role_patch
    @modulestore_patch
    def test_get_elm_credentials_with_invalid_query_params(
        self,
        modulestore_mock: Mock,
        course_staff_role_mock: Mock,
        course_instructor_role_mock: Mock,
    ):
        """Test GET request for Elm credentials with invalid query params."""
        modulestore_mock.return_value.get_course.return_value = self.get_course
        course_staff_role_mock.has_user.return_value = True
        course_instructor_role_mock.has_user.return_value = True

        self.request = self.factory.get(
            self.url, {"expires_at": "25-25-25", "to_file": 100}
        )
        force_authenticate(self.request, user=self.request_user)
        response = self.view(self.request, course_id=self.course_id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expires_at", response.data["field_errors"])
        self.assertIn("to_file", response.data["field_errors"])
