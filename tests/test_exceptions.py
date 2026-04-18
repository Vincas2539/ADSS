"""
Tests for custom exception classes.
"""

import pytest
from adss.exceptions import (
    ADSSClientError,
    AuthenticationError,
    PermissionDeniedError,
    ResourceNotFoundError,
    QueryExecutionError,
    ValidationError,
    ConnectionError,
)


class TestADSSClientError:
    """Tests for the base ADSSClientError."""

    def test_exception_creation_with_message(self):
        """Test creating an exception with a message."""
        message = "Something went wrong"
        exc = ADSSClientError(message)

        assert str(exc) == message
        assert exc.message == message

    def test_exception_creation_with_response(self):
        """Test creating an exception with response."""
        message = "Error"
        response = {"status": 400}
        exc = ADSSClientError(message, response)

        assert exc.message == message
        assert exc.response == response

    def test_exception_is_subclass_of_exception(self):
        """Test that ADSSClientError is an Exception."""
        assert issubclass(ADSSClientError, Exception)


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_authentication_error_creation(self):
        """Test creating an AuthenticationError."""
        message = "Invalid credentials"
        exc = AuthenticationError(message)

        assert str(exc) == message
        assert isinstance(exc, ADSSClientError)

    def test_authentication_error_with_response(self):
        """Test creating AuthenticationError with response."""
        message = "Auth failed"
        response = {"detail": "Invalid token"}
        exc = AuthenticationError(message, response)

        assert exc.response == response


class TestPermissionDeniedError:
    """Tests for PermissionDeniedError."""

    def test_permission_denied_error_creation(self):
        """Test creating a PermissionDeniedError."""
        message = "Insufficient permissions"
        exc = PermissionDeniedError(message)

        assert str(exc) == message
        assert isinstance(exc, ADSSClientError)


class TestResourceNotFoundError:
    """Tests for ResourceNotFoundError."""

    def test_resource_not_found_error_creation(self):
        """Test creating a ResourceNotFoundError."""
        message = "Query not found"
        exc = ResourceNotFoundError(message)

        assert str(exc) == message
        assert isinstance(exc, ADSSClientError)


class TestQueryExecutionError:
    """Tests for QueryExecutionError."""

    def test_query_execution_error_creation(self):
        """Test creating a QueryExecutionError."""
        message = "Query failed"
        exc = QueryExecutionError(message)

        assert str(exc) == message
        assert exc.query is None

    def test_query_execution_error_with_query(self):
        """Test creating QueryExecutionError with query information."""
        message = "Syntax error"
        query = "SELECT * FROM invalid_table"
        exc = QueryExecutionError(message, query=query)

        assert exc.message == message
        assert exc.query == query

    def test_query_execution_error_with_response(self):
        """Test creating QueryExecutionError with response."""
        message = "Query execution failed"
        response = {"error": "timeout"}
        exc = QueryExecutionError(message, response=response)

        assert exc.response == response


class TestValidationError:
    """Tests for ValidationError."""

    def test_validation_error_creation(self):
        """Test creating a ValidationError."""
        message = "Invalid input"
        exc = ValidationError(message)

        assert str(exc) == message
        assert exc.errors == {}

    def test_validation_error_with_errors(self):
        """Test creating ValidationError with error details."""
        message = "Validation failed"
        errors = {"field1": "Required field", "field2": "Invalid format"}
        exc = ValidationError(message, errors=errors)

        assert exc.errors == errors
        assert "field1" in exc.errors

    def test_validation_error_with_response(self):
        """Test creating ValidationError with response."""
        message = "Invalid data"
        errors = {"name": "Name is required"}
        response = {"errors": errors}
        exc = ValidationError(message, errors=errors, response=response)

        assert exc.response == response


class TestConnectionError:
    """Tests for ConnectionError."""

    def test_connection_error_creation(self):
        """Test creating a ConnectionError."""
        message = "Could not connect to server"
        exc = ConnectionError(message)

        assert str(exc) == message
        assert isinstance(exc, ADSSClientError)


class TestExceptionInheritance:
    """Tests for exception inheritance chain."""

    def test_all_custom_exceptions_inherit_from_adss_client_error(self):
        """Test that all custom exceptions inherit from ADSSClientError."""
        exceptions = [
            AuthenticationError,
            PermissionDeniedError,
            ResourceNotFoundError,
            QueryExecutionError,
            ValidationError,
            ConnectionError,
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, ADSSClientError)

    def test_all_exceptions_are_catchable_as_exception(self):
        """Test that exceptions can be caught as base Exception."""
        message = "Test"

        exceptions = [
            ADSSClientError(message),
            AuthenticationError(message),
            PermissionDeniedError(message),
            ResourceNotFoundError(message),
            QueryExecutionError(message),
            ValidationError(message),
            ConnectionError(message),
        ]

        for exc in exceptions:
            assert isinstance(exc, Exception)
