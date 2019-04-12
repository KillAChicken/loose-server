"""Test cases for MethodRule."""

import random

import pytest

from looseserver.default.common.constants import RuleType
from looseserver.default.common.configuration import RuleFactoryPreparator
from looseserver.default.server.rule import MethodRule


_METHODS = ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]


def test_rule_representation():
    """Check the representation of the method rule.

    1. Create a method rule.
    2. Check result of the repr function.
    """
    method = random.choice(_METHODS)
    rule = MethodRule(method=method, rule_type=RuleType.METHOD.name)
    assert repr(rule) == "MethodRule(method='{0}')".format(method), "Wrong representation"


@pytest.mark.parametrize(argnames="method", argvalues=_METHODS)
def test_match_found(
        base_endpoint,
        server_rule_factory,
        configured_application_client,
        apply_rule,
        method,
    ):
    """Check that MethodRule is triggered for the specified method.

    1. Prepare method rule in the rule factory.
    2. Create a method rule and set successful response for it.
    3. Make a request of the specified type.
    4. Check that the rule finds a match.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_method_rule(method_rule_class=MethodRule)

    rule = MethodRule(rule_type=RuleType.METHOD.name, method=method)
    apply_rule(rule)

    http_response = configured_application_client.open(base_endpoint, method=method)
    assert http_response.status_code == 200, "Wrong status code"


@pytest.mark.parametrize(argnames="method", argvalues=_METHODS)
def test_no_match(
        base_endpoint,
        server_rule_factory,
        configured_application_client,
        apply_rule,
        method,
    ):
    """Check that MethodRule is not triggered for different methods.

    1. Prepare method rule in the rule factory.
    2. Create a method rule and set successful response for it.
    3. Make a request of different types.
    4. Check that the rule does not find a match for any of the requests.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_method_rule(method_rule_class=MethodRule)

    rule = MethodRule(rule_type=RuleType.METHOD.name, method=method)
    apply_rule(rule)

    method_responses = [
        configured_application_client.open(base_endpoint, method=wrong_method)
        for wrong_method in _METHODS if wrong_method != method
        ]
    assert all(method_response.status_code == 404 for method_response in method_responses), (
        "Match found for at least one of the other methods"
        )
