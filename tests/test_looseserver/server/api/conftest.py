"""Configuration of pytest."""

import pytest


# pylint: disable=redefined-outer-name
@pytest.fixture
def registered_rule_prototype(rule_factory, server_rule_prototype):
    """Rule that can be parsed and serialized."""
    rule_type = "TestType"
    parser = lambda rule_type, rule_data: server_rule_prototype.create_new(rule_type=rule_type)
    serializer = lambda rule_type, rule: {"key": "value"}

    rule_factory.register_rule(rule_type=rule_type, parser=parser, serializer=serializer)

    return server_rule_prototype.create_new(rule_type=rule_type)


@pytest.fixture
def registered_response_prototype(response_factory, server_response_prototype):
    """Response that can be parsed and serialized."""
    response_type = "TestType"
    parser = lambda response_type, response_data: server_response_prototype.create_new(
        response_type=response_type,
        )
    serializer = lambda response_type, response: {"key": "value"}

    response_factory.register_response(
        response_type=response_type,
        parser=parser,
        serializer=serializer,
        )

    return server_response_prototype.create_new(response_type=response_type)
# pylint: enable=redefined-outer-name
