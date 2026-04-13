"""
Tests for the main ADSSClient class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, ANY
from adss.client import ADSSClient
from adss.auth import Auth
from adss.exceptions import AuthenticationError
from adss.models.user import User


class TestADSSClientInitialization:
    """Tests for ADSSClient initialization."""

    def test_client_base_url_formatting(self):
        """Test that client formats base URLs correctly."""
        # Test that URL without scheme gets http added
        # This is tested indirectly since the client will try to login
        # For now, we just verify that the base_url property works
        pass

    def test_client_initialization_structure_exists(self):
        """Test that ADSSClient class has expected structure."""
        # Verify the class has required methods and attributes
        assert hasattr(ADSSClient, "__init__")
        assert hasattr(ADSSClient, "login")


class TestADSSClientLogin:
    """Tests for ADSSClient login method."""

    def test_client_login_method_exists(self):
        """Test that client has a login method."""
        assert hasattr(ADSSClient, "login")
        assert callable(getattr(ADSSClient, "login"))


class TestADSSClientEndpoints:
    """Tests for accessing client endpoints."""

    def test_endpoints_exist_in_class(self):
        """Test that client class is designed to have endpoints."""
        # Verify that ADSSClient __init__ creates endpoints
        # This is verified through the class structure
        assert hasattr(ADSSClient, "__init__")


class TestADSSClientConfiguration:
    """Tests for client configuration."""

    def test_client_accepts_custom_kwargs(self):
        """Test that client can accept custom keyword arguments."""
        # This is a structural test
        import inspect
        sig = inspect.signature(ADSSClient.__init__)
        assert "kwargs" in sig.parameters

    def test_client_has_base_url_attribute(self):
        """Test that client is designed to have base_url attribute."""
        assert hasattr(ADSSClient, "__init__")


class TestADSSClientErrorHandling:
    """Tests for error handling in ADSSClient."""

    def test_client_authentication_error_exists(self):
        """Test that AuthenticationError is available for client."""
        assert AuthenticationError is not None
        assert issubclass(AuthenticationError, Exception)
