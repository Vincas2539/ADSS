"""
Shared fixtures and configuration for tests.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture
def mock_user_dict():
    """Fixture for a mock user dictionary."""
    return {
        "id": "user123",
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "is_staff": False,
        "is_superuser": False,
        "created_at": "2024-01-01T10:00:00Z",
        "last_login": "2024-01-15T14:30:00Z",
        "roles": [],
    }


@pytest.fixture
def mock_query_dict():
    """Fixture for a mock query dictionary."""
    return {
        "id": "query123",
        "query_text": "SELECT * FROM schema.table",
        "status": "completed",  # lowercase
        "mode": "adql",
        "user_id": "user123",
        "created_at": "2024-01-15T10:00:00Z",
        "completed_at": "2024-01-15T10:05:00Z",
        "result_url": "https://api.example.com/results/query123",
        "error": None,
        "execution_time_ms": 5000,
        "row_count": 1000,
        "position_in_queue": None,
        "expires_at": "2024-02-15T10:00:00Z",
        "query_metadata": {"table": "stars"},
    }


@pytest.fixture
def mock_role_dict():
    """Fixture for a mock role dictionary."""
    return {
        "id": 1,
        "name": "astronomer",
        "description": "Astronomer role with read access",
        "permissions": {
            "schema_permissions": [
                {"schema_name": "public", "permission": "read"}
            ],
            "table_permissions": [
                {
                    "schema_name": "public",
                    "table_name": "stars",
                    "permission": "read",
                }
            ],
        },
    }


@pytest.fixture
def mock_http_response():
    """Fixture for a mock HTTP response."""
    response = MagicMock()
    response.status_code = 200
    response.headers = {"Content-Type": "application/json"}
    response.text = '{"success": true}'
    return response


@pytest.fixture
def mock_base_url():
    """Fixture for a base API URL."""
    return "https://api.example.com"


@pytest.fixture
def mock_username():
    """Fixture for a test username."""
    return "testuser"


@pytest.fixture
def mock_password():
    """Fixture for a test password."""
    return "testpass123"


@pytest.fixture
def mock_auth(mock_base_url):
    """Fixture for a mocked Auth instance."""
    with patch("adss.auth.Auth") as MockAuth:
        auth = Mock()
        auth.base_url = mock_base_url
        auth.token = "mock_token_abc123"
        auth.user = None
        MockAuth.return_value = auth
        yield auth


@pytest.fixture
def sample_datetime_str():
    """Fixture for a sample ISO datetime string."""
    return "2024-01-15T10:30:45Z"


@pytest.fixture
def sample_parquet_bytes():
    """Fixture for sample parquet bytes."""
    import io
    import pyarrow as pa
    import pyarrow.parquet as pq

    # Create a simple table
    data = {"name": ["Alice", "Bob"], "age": [25, 30]}
    table = pa.table(data)

    # Write to bytes
    buf = io.BytesIO()
    pq.write_table(table, buf)
    return buf.getvalue()
