"""Unit tests for core auth behavior and helpers."""

from unittest.mock import Mock, patch

import httpx
import pytest

from adss.auth import Auth, _attach_requests_compat, _read_all_bytes, _to_httpx_timeout
from adss.exceptions import AuthenticationError

class _DummyStreamingResponse:
    """Small response test double with deterministic attribute behavior."""

    def __init__(self, chunks=None, headers=None):
        self._chunks = list(chunks or [])
        self.headers = headers or {}
        self.close = Mock()

    def iter_bytes(self, chunk_size=1024 * 1024):
        del chunk_size
        return iter(self._chunks)


def _streaming_response(chunks=None, headers=None):
    return _DummyStreamingResponse(chunks=chunks, headers=headers)


class TestAuthCore:
    def test_get_auth_headers_without_token(self, mock_base_url):
        auth = Auth(mock_base_url)
        headers = auth._get_auth_headers()

        assert headers == {"Accept": "application/json"}

    def test_get_auth_headers_with_token(self, mock_base_url):
        auth = Auth(mock_base_url)
        auth.token = "abc"

        headers = auth._get_auth_headers()
        assert headers["Authorization"] == "Bearer abc"

    def test_full_url_with_relative_and_absolute(self, mock_base_url):
        auth = Auth(mock_base_url)

        assert auth._full_url("adss/v1/users/me") == f"{mock_base_url}/adss/v1/users/me"
        assert auth._full_url("https://example.org/path") == "https://example.org/path"

    def test_request_requires_authentication(self, mock_base_url):
        auth = Auth(mock_base_url)

        with pytest.raises(AuthenticationError):
            auth.request("GET", "/adss/v1/users/me", auth_required=True)

    def test_request_nonstream_uses_client_request(self, mock_base_url):
        auth = Auth(mock_base_url)
        resp = _streaming_response(chunks=[b"ok"], headers={"Content-Length": "2"})
        auth._client.request = Mock(return_value=resp)

        result = auth.request(
            method="get",
            url="/adss/v1/ping",
            headers={"X-Test": "1"},
            allow_redirects=False,
            timeout=(1, 2),
            params={"a": 1},
        )

        auth._client.request.assert_called_once()
        _, kwargs = auth._client.request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["follow_redirects"] is False
        assert kwargs["params"] == {"a": 1}
        assert callable(getattr(result, "iter_content"))

    def test_login_sets_token_and_current_user(self, mock_base_url):
        auth = Auth(mock_base_url)
        fake_user = Mock()
        fake_response = Mock(status_code=200)
        fake_response.json.return_value = {"access_token": "token-1"}

        with patch("adss.auth.handle_response_errors") as mock_handler:
            mock_handler.return_value = fake_response
            with patch.object(auth, "request", return_value=fake_response):
                with patch.object(auth, "_get_current_user", return_value=fake_user):
                    token, user = auth.login("u", "p")

        assert token == "token-1"
        assert user is fake_user
        assert auth.current_user is fake_user

    def test_login_without_token_raises(self, mock_base_url):
        auth = Auth(mock_base_url)
        fake_response = Mock(status_code=200)
        fake_response.json.return_value = {}

        with patch("adss.auth.handle_response_errors") as mock_handler:
            mock_handler.return_value = fake_response
            with patch.object(auth, "request", return_value=fake_response):
                with pytest.raises(AuthenticationError):
                    auth.login("u", "p")

    def test_download_bytes_reads_stream(self, mock_base_url):
        auth = Auth(mock_base_url)
        resp = _streaming_response(chunks=[b"ab", b"cd"], headers={"Content-Length": "4"})

        with patch.object(auth, "_request_with_retries_stream", return_value=resp):
            with patch("adss.auth.handle_response_errors"):
                data = auth.download_bytes("GET", "/file", auth_required=False)

        assert data == b"abcd"
        resp.close.assert_called_once()


class TestAuthHelpers:
    def test_to_httpx_timeout_from_tuple(self):
        timeout = _to_httpx_timeout((2, 7))
        assert isinstance(timeout, httpx.Timeout)
        assert timeout.connect == 2
        assert timeout.read == 7

    def test_read_all_bytes_content_length_mismatch(self):
        resp = _streaming_response(chunks=[b"abc"], headers={"Content-Length": "4"})

        with pytest.raises(httpx.RemoteProtocolError):
            _read_all_bytes(resp)

        resp.close.assert_called_once()

    def test_attach_requests_compat_read_is_idempotent(self):
        resp = _streaming_response(chunks=[b"12", b"34"], headers={"Content-Length": "4"})
        wrapped = _attach_requests_compat(resp)

        first = wrapped.read()
        second = wrapped.read()

        assert first == b"1234"
        assert second == b"1234"
        wrapped.close.assert_called_once()