"""Test cases for looseserver client responses."""

from looseserver.client.response import ClientResponse


def test_response_type():
    """Check that response type can be obtained.

    1. Create instance of the class.
    2. Check the type of the response.
    """
    response = ClientResponse(response_type="test")
    assert response.response_type == "test", "Wrong response type"
