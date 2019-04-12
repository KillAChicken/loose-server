"""Configuration of pytest."""

import pytest

from looseserver.client.rule import ClientRule
from looseserver.client.response import ClientResponse


@pytest.fixture
def registered_rule(server_rule_factory, client_rule_factory, server_rule_prototype):
    """Client rule of a registered type."""
    rule_type = "CLIENT_RULE"

    def _create_server_rule():
        return server_rule_prototype.create_new(
            rule_type=rule_type,
            match_implementation=lambda *args, **kwargs: True,
            )

    server_rule_factory.register_rule(
        rule_type=rule_type,
        parser=lambda *args, **kwargs: _create_server_rule(),
        serializer=lambda *args, **kwargs: {}
        )

    client_rule_factory.register_rule(
        rule_type=rule_type,
        parser=lambda *args, **kwargs: ClientRule(rule_type=rule_type),
        serializer=lambda *args, **kwargs: {}
        )

    return ClientRule(rule_type=rule_type)


@pytest.fixture
def registered_response(
        server_response_factory,
        client_response_factory,
        server_response_prototype,
    ):
    """Client response of a registered type."""
    response_type = "CLIENT_RESPONSE"

    def _create_server_response():
        return server_response_prototype.create_new(
            response_type=response_type,
            builder_implementation=lambda *args, **kwargs: b"body",
            )

    server_response_factory.register_response(
        response_type=response_type,
        parser=lambda *args, **kwargs: _create_server_response(),
        serializer=lambda *args, **kwargs: {}
        )

    client_response_factory.register_response(
        response_type=response_type,
        parser=lambda *args, **kwargs: ClientResponse(response_type=response_type),
        serializer=lambda *args, **kwargs: {}
        )

    return ClientResponse(response_type=response_type)
