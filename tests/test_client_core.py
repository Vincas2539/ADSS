"""Unit tests for ADSSClient core orchestration and delegations."""

from unittest.mock import Mock, patch

import pytest

from adss.client import ADSSClient
from adss.exceptions import AuthenticationError


def _new_client_with_mocks():
    client = ADSSClient.__new__(ADSSClient)
    client.base_url = "https://api.example.com"
    client.auth = Mock()
    client.queries = Mock()
    client.users = Mock()
    client.metadata = Mock()
    client.admin = Mock()
    client.images = Mock()
    client.lupton_images = Mock()
    client.stamp_images = Mock()
    client.trilogy_images = Mock()
    return client


class TestClientInit:
    @patch("adss.client.TrilogyImagesEndpoint")
    @patch("adss.client.StampImagesEndpoint")
    @patch("adss.client.LuptonImagesEndpoint")
    @patch("adss.client.ImagesEndpoint")
    @patch("adss.client.MetadataEndpoint")
    @patch("adss.client.UsersEndpoint")
    @patch("adss.client.QueriesEndpoint")
    @patch("adss.client.Auth")
    def test_init_adds_scheme_and_initializes_dependencies(
        self,
        mock_auth,
        mock_queries,
        mock_users,
        mock_metadata,
        mock_images,
        mock_lupton,
        mock_stamp,
        mock_trilogy,
    ):
        auth_instance = Mock()
        auth_instance.login.return_value = ("tok", Mock())
        mock_auth.return_value = auth_instance

        client = ADSSClient("api.example.com", username="user", password="pass")

        assert client.base_url == "http://api.example.com"
        mock_auth.assert_called_once()
        mock_queries.assert_called_once()
        mock_users.assert_called_once()
        mock_metadata.assert_called_once()
        mock_images.assert_called_once()
        mock_lupton.assert_called_once()
        mock_stamp.assert_called_once()
        mock_trilogy.assert_called_once()
        auth_instance.login.assert_called_once_with("user", "pass")

    @patch("urllib3.disable_warnings")
    @patch("adss.client.TrilogyImagesEndpoint")
    @patch("adss.client.StampImagesEndpoint")
    @patch("adss.client.LuptonImagesEndpoint")
    @patch("adss.client.ImagesEndpoint")
    @patch("adss.client.MetadataEndpoint")
    @patch("adss.client.UsersEndpoint")
    @patch("adss.client.QueriesEndpoint")
    @patch("adss.client.Auth")
    def test_init_disables_insecure_warning_when_ssl_off(
        self,
        mock_auth,
        _mock_queries,
        _mock_users,
        _mock_metadata,
        _mock_images,
        _mock_lupton,
        _mock_stamp,
        _mock_trilogy,
        mock_disable_warnings,
    ):
        auth_instance = Mock()
        auth_instance.login.return_value = ("tok", Mock())
        mock_auth.return_value = auth_instance

        ADSSClient(
            "https://api.example.com",
            username="user",
            password="pass",
            verify_ssl=False,
        )

        mock_disable_warnings.assert_called_once()


class TestClientBehavior:
    def test_properties_delegate_to_auth(self):
        client = _new_client_with_mocks()
        client.auth.is_authenticated.return_value = True
        client.auth.current_user = Mock()

        assert client.is_authenticated is True
        assert client.current_user is client.auth.current_user

    def test_query_history_requires_authentication(self):
        client = _new_client_with_mocks()
        client.auth.is_authenticated.return_value = False

        with pytest.raises(AuthenticationError):
            client.get_query_history()

    def test_query_history_delegates_when_authenticated(self):
        client = _new_client_with_mocks()
        client.auth.is_authenticated.return_value = True
        expected = [Mock()]
        client.queries.get_history.return_value = expected

        result = client.get_query_history(limit=10)

        assert result == expected
        client.queries.get_history.assert_called_once_with(10)

    def test_update_profile_requires_authentication(self):
        client = _new_client_with_mocks()
        client.auth.is_authenticated.return_value = False

        with pytest.raises(AuthenticationError):
            client.update_profile(email="x@y.com")

    def test_core_delegation_methods(self):
        client = _new_client_with_mocks()
        client.auth.is_authenticated.return_value = True
        client.auth.login.return_value = ("tok", Mock())

        client.login("u", "p")
        client.logout()
        client.register("u", "e@x.com", "p", "Name")
        client.query("select 1")
        client.async_query("select 1")
        client.get_query_status("q1")
        client.get_query_results("q1")
        client.cancel_query("q1")
        client.query_and_wait("select 1", timeout=1)

        client.auth.login.assert_called_once_with("u", "p")
        client.auth.logout.assert_called_once()
        client.users.register.assert_called_once_with("u", "e@x.com", "p", "Name")
        client.queries.execute_sync.assert_called_once()
        client.queries.execute_async.assert_called_once()
        client.queries.get_status.assert_called_once_with("q1")
        client.queries.get_results.assert_called_once_with("q1")
        client.queries.cancel_query.assert_called_once_with("q1")
        client.queries.execute_and_wait.assert_called_once()

    def test_metadata_and_pretty_print(self, capsys):
        client = _new_client_with_mocks()

        col = Mock(name="id", data_type="int", is_nullable=False)
        table = Mock(name="stars", columns=[col])
        schema = Mock(name="public", tables=[table])
        dbmeta = Mock(schemas=[schema])
        client.metadata.get_database_metadata.return_value = dbmeta

        client.get_schemas()
        client.get_tables("public")
        client.get_columns("public", "stars")
        result = client.get_database_metadata()
        client.pretty_print_db_metadata(result)

        out = capsys.readouterr().out
        assert "Schema:" in out
        assert "Table:" in out
        assert "Column:" in out
        client.metadata.get_schemas.assert_called_once()
        client.metadata.get_tables.assert_called_once_with("public")
        client.metadata.get_columns.assert_called_once_with("public", "stars")
        client.metadata.get_database_metadata.assert_called_once()

    def test_admin_and_images_delegate(self):
        client = _new_client_with_mocks()

        client.create_role("reader")
        client.get_roles()
        client.add_user_to_role("u1", 2)
        client.remove_user_from_role("u1", 2)
        client.add_schema_permission(2, "public", "read")
        client.add_table_permission(2, "public", "stars", "read")
        client.remove_schema_permission(2, "public")
        client.remove_table_permission(2, "public", "stars")
        client.get_role_permissions(2)

        client.get_collections()
        client.get_collection(1)
        client.list_files(1)
        client.cone_search_images(1, 1.0, 2.0, 0.1)
        client.download_file(5)
        client.create_rgb_image(1, 2, 3)
        client.create_rgb_image_by_coordinates(1, 1.0, 2.0, 3.0, "r", "g", "b")
        client.create_stamp(1, 1.0, 2.0, 3.0)
        client.create_stamp_by_coordinates(1, 1.0, 2.0, 3.0, "r")
        client.create_trilogy_rgb([1], [2], [3])

        client.admin.create_role.assert_called_once_with("reader", None)
        client.admin.get_roles.assert_called_once_with(0, 100)
        client.images.get_collections.assert_called_once()
        client.lupton_images.create_rgb.assert_called_once()
        client.stamp_images.create_stamp.assert_called_once()
        client.trilogy_images.create_trilogy_rgb.assert_called_once()