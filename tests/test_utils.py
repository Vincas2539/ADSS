"""
Tests for utility functions.
"""

import pytest
from datetime import datetime
from adss.utils import (
    parse_datetime,
    parquet_to_dataframe,
    format_table_name,
    prepare_query_params,
    handle_response_errors,
)
from adss.exceptions import (
    AuthenticationError,
    PermissionDeniedError,
    ResourceNotFoundError,
    ADSSClientError,
)
from unittest.mock import Mock


class TestParseDatetime:
    """Tests for the parse_datetime utility."""

    def test_parse_valid_iso_datetime(self, sample_datetime_str):
        """Test parsing a valid ISO format datetime string."""
        result = parse_datetime(sample_datetime_str)

        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_iso_datetime_with_z_suffix(self):
        """Test parsing ISO datetime with Z suffix."""
        result = parse_datetime("2024-01-15T10:30:45Z")

        assert isinstance(result, datetime)
        assert result.hour == 10
        assert result.minute == 30
        assert result.second == 45

    def test_parse_none_returns_none(self):
        """Test that parsing None returns None."""
        result = parse_datetime(None)
        assert result is None

    def test_parse_empty_string_returns_none(self):
        """Test that parsing empty string returns None."""
        result = parse_datetime("")
        assert result is None

    def test_parse_invalid_datetime_returns_none(self):
        """Test that parsing invalid datetime returns None."""
        result = parse_datetime("invalid-date")
        assert result is None

    def test_parse_iso_datetime_without_z(self):
        """Test parsing ISO datetime without Z suffix."""
        result = parse_datetime("2024-01-15T10:30:45")
        assert isinstance(result, datetime)


class TestParquetToDataframe:
    """Tests for parquet_to_dataframe utility."""

    def test_convert_valid_parquet_bytes(self, sample_parquet_bytes):
        """Test converting valid parquet bytes to DataFrame."""
        import pandas as pd

        df = parquet_to_dataframe(sample_parquet_bytes)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ["name", "age"]
        assert list(df["name"]) == ["Alice", "Bob"]
        assert list(df["age"]) == [25, 30]

    def test_convert_invalid_parquet_bytes(self):
        """Test that invalid parquet bytes raise an error."""
        from adss.exceptions import ADSSClientError

        invalid_bytes = b"not a parquet file"

        with pytest.raises(ADSSClientError):
            parquet_to_dataframe(invalid_bytes)

    def test_convert_empty_parquet_bytes(self):
        """Test that empty bytes raise an error."""
        from adss.exceptions import ADSSClientError

        with pytest.raises(ADSSClientError):
            parquet_to_dataframe(b"")


class TestFormatTableName:
    """Tests for format_table_name utility."""

    def test_format_valid_table_name(self):
        """Test formatting a valid table name."""
        result = format_table_name("public", "stars")
        assert result == "public.stars"

    def test_format_table_name_with_special_chars(self):
        """Test formatting table name with special characters."""
        result = format_table_name("my_schema", "my_table_data")
        assert result == "my_schema.my_table_data"


class TestPrepareQueryParams:
    """Tests for prepare_query_params utility."""

    def test_prepare_params_with_various_types(self):
        """Test preparing query params with different data types."""
        params = {
            "string_param": "value",
            "int_param": 42,
            "bool_param": True,
            "none_param": None,
            "list_param": [1, 2, 3],
            "dict_param": {"key": "value"},
        }

        result = prepare_query_params(params)

        assert result["string_param"] == "value"
        assert result["int_param"] == "42"  # converted to string
        assert result["bool_param"] == "true"
        assert "none_param" not in result  # None values are skipped
        assert result["list_param"] is not None  # json.dumps returns string
        assert result["dict_param"] is not None

    def test_prepare_params_filters_none_values(self):
        """Test that None values are filtered out."""
        params = {"key1": "value", "key2": None, "key3": "another"}
        result = prepare_query_params(params)

        assert "key1" in result
        assert "key2" not in result
        assert "key3" in result

    def test_prepare_params_boolean_conversion(self):
        """Test that booleans are converted to lowercase strings."""
        params = {"bool_true": True, "bool_false": False}
        result = prepare_query_params(params)

        assert result["bool_true"] == "true"
        assert result["bool_false"] == "false"


class TestHandleResponseErrors:
    """Tests for handle_response_errors utility."""

    def test_handle_success_response(self):
        """Test that successful responses are returned unchanged."""
        response = Mock()
        response.status_code = 200

        result = handle_response_errors(response)
        assert result == response

    def test_handle_401_authentication_error(self):
        """Test that 401 responses raise AuthenticationError."""
        response = Mock()
        response.status_code = 401
        response.read.return_value = {"detail": "Invalid credentials"}

        with pytest.raises(AuthenticationError):
            handle_response_errors(response)

    def test_handle_403_permission_denied_error(self):
        """Test that 403 responses raise PermissionDeniedError."""
        response = Mock()
        response.status_code = 403
        response.read.return_value = {"detail": "Access denied"}

        with pytest.raises(PermissionDeniedError):
            handle_response_errors(response)

    def test_handle_404_resource_not_found_error(self):
        """Test that 404 responses raise ResourceNotFoundError."""
        response = Mock()
        response.status_code = 404
        response.read.return_value = {"detail": "Resource not found"}

        with pytest.raises(ResourceNotFoundError):
            handle_response_errors(response)

    def test_handle_500_server_error(self):
        """Test that 500+ responses raise appropriate errors."""
        response = Mock()
        response.status_code = 500
        response.read.return_value = {"detail": "Internal server error"}

        with pytest.raises(ADSSClientError):
            handle_response_errors(response)

    def test_handle_response_with_non_json_body(self):
        """Test handling response when body is not JSON."""
        response = Mock()
        response.status_code = 400
        response.read.side_effect = Exception("Not JSON")
        response.text = "Bad Request"

        with pytest.raises(ADSSClientError):
            handle_response_errors(response)
