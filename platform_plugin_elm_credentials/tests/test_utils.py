"""Test utils functions of platform_plugin_elm_credentials."""
from unittest import TestCase

from ddt import data, ddt, unpack

from platform_plugin_elm_credentials.api.utils import get_filename, get_fullname, pydantic_error_to_response


@ddt
class TestUtils(TestCase):
    """Test utils functions."""

    @data(
        ("John", "Doe Roe", "John Doe Roe"),
        ("John", "Doe", "John Doe"),
        ("John", "", "John"),
        ("Doe", "", "Doe"),
        ("", "", ""),
    )
    @unpack
    def test_get_fullname(self, first_name, last_name, full_name):
        """Test `get_fullname` function."""
        result = get_fullname(full_name)
        self.assertTupleEqual((first_name, last_name), result)

    def test_pydantic_error_to_response(self):
        """Test `pydantic_error_to_response` function."""
        errors = [
            {"loc": ("expired_at",), "msg": "expired_at error"},
            {"loc": ("to_file",), "msg": "to_file message"},
        ]
        result = pydantic_error_to_response(errors)
        self.assertEqual(
            result, {"expired_at": "expired_at error", "to_file": "to_file message"}
        )

    def test_get_filename(self):
        """Test `get_filename` function."""
        course_id = "course-v1:edX+DemoX+Demo_Course"
        result = get_filename(course_id)
        self.assertEqual(result, "credentials-course-v1_edX+DemoX+Demo_Course.zip")

        user = "test_user"
        result = get_filename(course_id, user)
        self.assertEqual(
            result, "credential-test_user-course-v1_edX+DemoX+Demo_Course.json"
        )
