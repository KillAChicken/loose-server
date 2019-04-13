"""Test cases for looseserver common API entities."""

from looseserver.common.api import APIError


def test_api_error_description():
    """Check description attribute of the API error.

    1. Create API error.
    2. Check error description.
    """
    error = APIError("description")
    assert error.description == "description", "Wrong description"
