"""Test cases for the build_response method."""

from looseserver.common.api import DEFAULT_VERSION, ResponseStatus, APIError
from looseserver.server.api import build_response


def test_version():
    """Check that version is included to the response.

    1. Build a response.
    2. Check that version is included.
    """
    version = DEFAULT_VERSION + 1
    response = build_response(version=version)
    assert response.get("version") == version, "Wrong version is set"


def test_default_version():
    """Check default version.

    1. Build a response.
    2. Check the default version.
    """
    response = build_response()
    assert response.get("version") == DEFAULT_VERSION, "Wrong version is set"


def test_success_without_data():
    """Check status and fields of a successful response.

    1. Build a response without error and data.
    2. Check the status.
    3. Check data fields.
    """
    response = build_response(error=None, data=None)
    assert response["status"] == ResponseStatus.SUCCESS.name, "Wrong status"
    assert "error" not in response, "Error field is present in a successful response"
    assert "data" not in response, "Data have been set"


def test_success_with_data():
    """Check status and fields of a successful response.

    1. Build a response without error.
    2. Check the status.
    3. Check data fields.
    """
    data = {}
    response = build_response(error=None, data=data)
    assert response["status"] == ResponseStatus.SUCCESS.name, "Wrong status"
    assert "error" not in response, "Error field is present in a successful response"
    assert response.get("data") == data, "Data have not been set"


def test_error_without_data():
    """Check status and fields of a failed response.

    1. Build a response with error, but without data.
    2. Check the status.
    3. Check data fields.
    """
    error = APIError("Test")
    response = build_response(error=error, data=None)
    assert response["status"] == ResponseStatus.FAILURE.name, "Wrong status"
    assert response["error"]["description"] == error.description, "Wrong error data"
    assert "data" not in response, "Data have been set"


def test_error_with_data():
    """Check status and fields of a failed response.

    1. Build a response without error.
    2. Check the status.
    3. Check data fields.
    """
    data = {}
    error = APIError("Test")
    response = build_response(error=error, data=data)
    assert response["status"] == ResponseStatus.FAILURE.name, "Wrong status"
    assert response["error"]["description"] == error.description, "Wrong error data"
    assert response.get("data") == data, "Data have not been set"
