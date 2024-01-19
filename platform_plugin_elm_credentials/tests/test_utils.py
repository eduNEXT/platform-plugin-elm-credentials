"""Test utils functions.""" ""
from unittest import TestCase

from ddt import data, ddt, unpack

from platform_plugin_elm_credentials.api.utils import get_fullname


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
