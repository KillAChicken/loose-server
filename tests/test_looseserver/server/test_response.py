"""Test cases for looseserver server responses."""

from looseserver.server.response import ServerResponse


def test_response_type():
    """Check that response type can be obtained.

    1. Create class for a response.
    2. Create instance of the class.
    3. Check the type of the response.
    """
    class Response(ServerResponse):
        """Test response."""
        def build_response(self, request, rule):
            """Test implementation."""

    response = Response(response_type="test")
    assert response.response_type == "test", "Wrong response type"
