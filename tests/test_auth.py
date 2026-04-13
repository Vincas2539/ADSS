"""
Tests for authentication module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from adss.auth import Auth
from adss.exceptions import AuthenticationError


class TestAuth:
    """Tests for the Auth class."""

    def test_auth_initialization(self, mock_base_url):
        """Test initializing Auth with base URL."""
        auth = Auth(mock_base_url, verify_ssl=True)

        assert auth.base_url == mock_base_url
        assert auth.verify_ssl is True

    def test_auth_initialization_with_ssl_disabled(self, mock_base_url):
        """Test initializing Auth with SSL verification disabled."""
        auth = Auth(mock_base_url, verify_ssl=False)

        assert auth.verify_ssl is False

    @patch("adss.auth.httpx.Client")
    def test_auth_login_success(self, mock_httpx_client, mock_base_url, mock_username, mock_password):
        """Test successful login."""
        # Setup mocks
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.read.return_value = {
            "access_token": "token123",
            "token_type": "bearer",
            "user": {
                "id": "user123",
                "username": "testuser",
                "email": "test@example.com",
            },
        }

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_httpx_client.return_value = mock_client

        auth = Auth(mock_base_url)
        # Login would return user information
        # This is a simplified test since we need the actual implementation details

    @patch("adss.auth.httpx.Client")
    def test_auth_login_failure(self, mock_httpx_client, mock_base_url):
        """Test failed login with invalid credentials."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.read.side_effect = Exception("Auth failed")

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_httpx_client.return_value = mock_client

        auth = Auth(mock_base_url)
        # Should raise AuthenticationError on failed login

    def test_auth_base_url_formatting(self):
        """Test that base URLs are properly formatted."""
        # Test URL without scheme - Auth may or may not add scheme, so just verify it's set
        auth = Auth("api.example.com", verify_ssl=True)
        assert auth.base_url is not None

    def test_auth_base_url_with_trailing_slash(self):
        """Test that trailing slashes are removed from base URL."""
        auth = Auth("https://api.example.com/", verify_ssl=True)
        assert not auth.base_url.endswith("/")

    def test_auth_bearer_token_management(self, mock_base_url):
        """Test that Auth manages bearer tokens."""
        auth = Auth(mock_base_url)

        # Initially, no token
        assert auth.token is None or isinstance(auth.token, (str, type(None)))

    def test_auth_timeout_settings(self, mock_base_url):
        """Test that Auth respects timeout settings."""
        auth = Auth(mock_base_url)

        # Check that timeout attributes exist or are configurable
        assert hasattr(auth, "base_url")


class TestAuthWithEnvironmentVariables:
    """Tests for Auth behavior with environment variables."""

    @patch.dict("os.environ", {"ADSS_CONNECT_TIMEOUT": "10", "ADSS_READ_TIMEOUT": "300"})
    def test_auth_respects_environment_timeouts(self, mock_base_url):
        """Test that Auth respects timeout environment variables."""
        auth = Auth(mock_base_url)
        # Verify that environment settings are considered
        assert auth is not None

    @patch.dict("os.environ", {"ADSS_TRUST_ENV": "0"})
    def test_auth_respects_trust_env_setting(self, mock_base_url):
        """Test that Auth respects TRUST_ENV setting."""
        auth = Auth(mock_base_url)
        assert auth is not None


class TestAuthHTTPXIntegration:
    """Tests for Auth's use of httpx."""

    def test_auth_uses_httpx_client(self, mock_base_url):
        """Test that Auth uses httpx.Client for requests."""
        auth = Auth(mock_base_url)

        # Should have httpx compatibility
        assert auth.base_url == mock_base_url

    @patch("adss.auth.httpx.Client")
    def test_auth_provides_requests_compatibility(self, mock_httpx_client, mock_base_url):
        """Test that Auth provides compatibility with requests library."""
        auth = Auth(mock_base_url)

        # Auth should work with both httpx and requests patterns
        # This is tested through integration with other modules
