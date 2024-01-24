"""Test serializers of platform_plugin_elm_credentials."""
from unittest import TestCase

from ddt import data, ddt, unpack

from platform_plugin_elm_credentials.api.serializers import QueryParamsModel


@ddt
class TestSerializers(TestCase):
    """Test serializers of platform_plugin_elm_credentials."""

    mock_expires_at = "2021-01-01T00:00:00+00:00"

    @data(
        (
            {"username": "john_doe"},
            {"username": "john_doe", "expires_at": None, "to_file": True},
        ),
        (
            {"username": "john_doe", "to_file": False},
            {"username": "john_doe", "expires_at": None, "to_file": False},
        ),
        (
            {"username": "john_doe", "expires_at": mock_expires_at},
            {"username": "john_doe", "expires_at": mock_expires_at, "to_file": True},
        ),
        (
            {"username": "john_doe", "expires_at": mock_expires_at, "to_file": True},
            {"username": "john_doe", "expires_at": mock_expires_at, "to_file": True},
        ),
        (
            {"username": "john_doe", "expires_at": mock_expires_at, "to_file": False},
            {"username": "john_doe", "expires_at": mock_expires_at, "to_file": False},
        ),
    )
    @unpack
    def test_query_params(self, query_params, expected):
        """Test QueryParamsModel serializer."""
        query_params = QueryParamsModel(**query_params)
        dumped_params = query_params.model_dump()
        self.assertEqual(expected["to_file"], dumped_params["to_file"])
        self.assertEqual(expected["expires_at"], dumped_params["expires_at"])
