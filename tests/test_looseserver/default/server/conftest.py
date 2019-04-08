"""Configuration of pytest."""

import pytest


@pytest.fixture
def response_200(response_factory, server_response_prototype):
    """Registered empty successful response."""
    response = server_response_prototype.create_new(
        response_type="RESPONSE200",
        builder_implementation=lambda *args, **kwargs: b""
        )

    response_factory.register_response(
        response_type=response.response_type,
        parser=lambda *args, **kwargs: response,
        serializer=lambda *args, **kwargs: {},
        )

    return response
