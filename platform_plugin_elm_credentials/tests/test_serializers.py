"""Test serializers of platform_plugin_elm_credentials."""
from unittest import TestCase

from ddt import data, ddt, unpack

from platform_plugin_elm_credentials.api.serializers import QueryParamsModel


@ddt
class TestSerializers(TestCase):
    """Test serializers of platform_plugin_elm_credentials."""

    mock_expired_at = "2021-01-01T00:00:00+00:00"

    @data(
        (
            {},
            {"expired_at": None, "to_file": True},
        ),
        (
            {"to_file": False},
            {"expired_at": None, "to_file": False},
        ),
        (
            {"expired_at": mock_expired_at},
            {"expired_at": mock_expired_at, "to_file": True},
        ),
        (
            {"expired_at": mock_expired_at, "to_file": True},
            {"expired_at": mock_expired_at, "to_file": True},
        ),
        (
            {"expired_at": mock_expired_at, "to_file": False},
            {"expired_at": mock_expired_at, "to_file": False},
        ),
    )
    @unpack
    def test_query_params(self, query_params, expected):
        """Test QueryParamsModel serializer."""
        query_params = QueryParamsModel(**query_params)
        dumped_params = query_params.model_dump()
        self.assertEqual(expected["to_file"], dumped_params["to_file"])
        self.assertEqual(expected["expired_at"], dumped_params["expired_at"])
