"""Configuration of pytest."""

import pytest


@pytest.fixture
def rule_match_all(rule_factory, server_rule_prototype):
    """Registered rule that matches every request."""
    rule = server_rule_prototype.create_new(
        rule_type="MATCHALL",
        match_implementation=lambda *args, **kwargs: True,
        )

    rule_factory.register_rule(
        rule_type=rule.rule_type,
        parser=lambda *args, **kwargs: rule,
        serializer=lambda *args, **kwargs: {},
        )

    return rule


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
