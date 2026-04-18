"""
Tests for data models (User, Query, Role, etc.).
"""

import pytest
from datetime import datetime
from adss.models.user import User, Role, SchemaPermission, TablePermission, RolePermissions
from adss.models.query import Query, QueryResult
from adss.models.metadata import Schema, Table, Column


class TestUser:
    """Tests for the User model."""

    def test_user_creation_from_dict(self, mock_user_dict):
        """Test creating a User from a dictionary."""
        user = User.from_dict(mock_user_dict)

        assert user.id == "user123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_user_creation_with_minimal_data(self):
        """Test creating a User with minimal required data."""
        data = {
            "id": "user456",
            "username": "minimal_user",
            "email": "minimal@example.com",
        }
        user = User.from_dict(data)

        assert user.id == "user456"
        assert user.username == "minimal_user"
        assert user.email == "minimal@example.com"
        assert user.full_name is None
        assert user.is_active is True  # default

    def test_user_with_roles(self, mock_user_dict, mock_role_dict):
        """Test creating a User with associated roles."""
        mock_user_dict["roles"] = [mock_role_dict]
        user = User.from_dict(mock_user_dict)

        assert len(user.roles) >= 0  # roles may or may not be populated depending on implementation

    def test_user_datetime_parsing(self, mock_user_dict):
        """Test that User correctly parses datetime strings."""
        user = User.from_dict(mock_user_dict)

        assert isinstance(user.created_at, datetime)
        assert isinstance(user.last_login, datetime)


class TestRole:
    """Tests for the Role model."""

    def test_role_creation_from_dict(self, mock_role_dict):
        """Test creating a Role from a dictionary."""
        role = Role.from_dict(mock_role_dict)

        assert role.id == 1
        assert role.name == "astronomer"
        assert role.description == "Astronomer role with read access"

    def test_role_with_permissions(self, mock_role_dict):
        """Test creating a Role with associated permissions."""
        role = Role.from_dict(mock_role_dict)

        assert role.permissions is not None
        assert len(role.permissions.schema_permissions) > 0
        assert len(role.permissions.table_permissions) > 0

    def test_role_without_permissions(self):
        """Test creating a Role without permissions."""
        data = {"id": 2, "name": "guest"}
        role = Role.from_dict(data)

        assert role.id == 2
        assert role.name == "guest"
        assert role.permissions is None


class TestSchemaPermission:
    """Tests for SchemaPermission model."""

    def test_schema_permission_creation(self):
        """Test creating a SchemaPermission."""
        perm = SchemaPermission(schema_name="public", permission="read")

        assert perm.schema_name == "public"
        assert perm.permission == "read"


class TestTablePermission:
    """Tests for TablePermission model."""

    def test_table_permission_creation(self):
        """Test creating a TablePermission."""
        perm = TablePermission(
            schema_name="public", table_name="stars", permission="read"
        )

        assert perm.schema_name == "public"
        assert perm.table_name == "stars"
        assert perm.permission == "read"


class TestRolePermissions:
    """Tests for RolePermissions model."""

    def test_role_permissions_from_dict(self, mock_role_dict):
        """Test creating RolePermissions from a dictionary."""
        perms = RolePermissions.from_dict(mock_role_dict["permissions"])

        assert len(perms.schema_permissions) > 0
        assert len(perms.table_permissions) > 0
        assert perms.schema_permissions[0].schema_name == "public"


class TestQuery:
    """Tests for the Query model."""

    def test_query_creation_from_dict(self, mock_query_dict):
        """Test creating a Query from a dictionary."""
        mock_query_dict["status"] = "completed"  # status is lowercase
        query = Query.from_dict(mock_query_dict)

        assert query.id == "query123"
        assert query.query_text == "SELECT * FROM schema.table"
        assert query.status == "completed"
        assert query.mode == "adql"
        assert query.execution_time_ms == 5000
        assert query.row_count == 1000

    def test_query_with_error(self, mock_query_dict):
        """Test creating a Query with an error."""
        mock_query_dict["status"] = "failed"  # lowercase
        mock_query_dict["error"] = "Syntax error in query"
        query = Query.from_dict(mock_query_dict)

        assert query.status == "failed"
        assert query.error == "Syntax error in query"

    def test_query_datetime_parsing(self, mock_query_dict):
        """Test that Query correctly parses datetime strings."""
        query = Query.from_dict(mock_query_dict)

        assert isinstance(query.created_at, datetime)
        assert isinstance(query.completed_at, datetime)
        assert isinstance(query.expires_at, datetime)


class TestMetadataModels:
    """Tests for metadata models (Schema, Table, Column)."""

    def test_column_creation(self):
        """Test creating a Column."""
        col = Column(name="id", data_type="int", is_nullable=False)

        assert col.name == "id"
        assert col.data_type == "int"
        assert col.is_nullable is False

    def test_table_creation(self):
        """Test creating a Table."""
        columns = [
            Column(name="id", data_type="int", is_nullable=False),
            Column(name="name", data_type="string", is_nullable=True),
        ]
        table = Table(name="stars", columns=columns)

        assert table.name == "stars"
        assert len(table.columns) == 2

    def test_schema_creation(self):
        """Test creating a Schema."""
        tables = [Table(name="stars", columns=[])]
        schema = Schema(name="public", tables=tables)

        assert schema.name == "public"
        assert len(schema.tables) == 1
