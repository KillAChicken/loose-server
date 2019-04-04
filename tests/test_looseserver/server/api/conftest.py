"""Configuration of pytest."""

import pytest

from looseserver.common.rule import RuleFactory
from looseserver.common.response import ResponseFactory


# pylint: disable=redefined-outer-name
@pytest.fixture
def rule_factory():
    """Rule factory."""
    return RuleFactory()


@pytest.fixture
def response_factory():
    """Response factory."""
    return ResponseFactory()


@pytest.fixture
def registered_rule_prototype(rule_factory, rule_prototype):
    """Rule that can be parsed and serialized."""
    rule_type = "TestType"
    parser = lambda rule_type, rule_data: rule_prototype.create_new(rule_type=rule_type)
    serializer = lambda rule_type, rule: {"key": "value"}

    rule_factory.register_rule(rule_type=rule_type, parser=parser, serializer=serializer)

    return rule_prototype.create_new(rule_type=rule_type)


@pytest.fixture
def registered_response_prototype(response_factory, response_prototype):
    """Response that can be parsed and serialized."""
    response_type = "TestType"
    parser = lambda response_type, response_data: response_prototype.create_new(response_type=response_type)    # pylint: disable=line-too-long
    serializer = lambda response_type, response: {"key": "value"}

    response_factory.register_response(
        response_type=response_type,
        parser=parser,
        serializer=serializer,
        )

    return response_prototype.create_new(response_type=response_type)
# pylint: enable=redefined-outer-name
