"""Test utils functions of platform_plugin_elm_credentials."""
from unittest import TestCase

from ddt import data, ddt, unpack

from platform_plugin_elm_credentials.api.utils import get_fullname, pydantic_error_to_response


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
        """Test get_fullname."""
        result = get_fullname(full_name)
        self.assertTupleEqual((first_name, last_name), result)

    def test_pydantic_error_to_response(self):
        """Test pydantic_error_to_response."""
        errors = [
            {"loc": ("expired_at",), "msg": "expired_at error"},
            {"loc": ("to_file",), "msg": "to_file message"},
        ]
        result = pydantic_error_to_response(errors)
        self.assertEqual(
            result, {"expired_at": "expired_at error", "to_file": "to_file message"}
        )
