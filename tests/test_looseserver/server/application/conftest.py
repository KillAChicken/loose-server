"""Configuration of pytest."""

import pytest


# pylint: disable=redefined-outer-name
@pytest.fixture
def registered_match_all_rule(server_rule_factory, server_rule_prototype):
    """Server rule of the registered type, matching every request."""
    rule_type = "MATCH_ALL"

    def _create_rule():
        return server_rule_prototype.create_new(
            rule_type=rule_type,
            match_implementation=lambda *args, **kwargs: True,
            )

    server_rule_factory.register_rule(
        rule_type=rule_type,
        parser=lambda *args, **kwargs: _create_rule(),
        serializer=lambda *args, **kwargs: {},
        )

    return _create_rule()


@pytest.fixture
def registered_response_data():
    """Body (bytes) of the registered response."""
    return b"response data"


@pytest.fixture
def registered_success_response(
        server_response_factory,
        server_response_prototype,
        registered_response_data,
    ):
    """Server success response of the registered type."""
    response_type = "TEST"

    def _create_response():
        return server_response_prototype.create_new(
            response_type=response_type,
            builder_implementation=lambda *args, **kwargs: registered_response_data,
            )

    server_response_factory.register_response(
        response_type=response_type,
        parser=lambda *args, **kwargs: _create_response(),
        serializer=lambda *args, **kwargs: {},
        )

    return _create_response()
# pylint: enable=redefined-outer-name
