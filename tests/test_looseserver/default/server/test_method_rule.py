"""Test cases for MethodRule."""

import random
from urllib.parse import urljoin

import pytest

from looseserver.server.application import configure_application
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
def test_match_found(rule_factory, response_factory, response_200, method):
    """Check that MethodRule is triggered for the specified method.

    1. Prepare method rule in the rule factory.
    2. Configure application with the rule factory.
    3. Make a POST-request to create a method rule.
    4. Set a response for the rule.
    5. Make a request of the specified type.
    6. Check that the rule finds a match.
    """
    base_endpoint = "/base/"
    configuration_endpoint = "/config/"

    preparator = RuleFactoryPreparator(rule_factory)
    preparator.prepare_method_rule(method_rule_class=MethodRule)

    application = configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        rule_factory=rule_factory,
        response_factory=response_factory,
        )

    rule = MethodRule(rule_type=RuleType.METHOD.name, method=method)
    serialized_rule = rule_factory.serialize_rule(rule=rule)

    client = application.test_client()

    http_response = client.post(urljoin(configuration_endpoint, "rules"), json=serialized_rule)

    assert http_response.status_code == 200, "Can't create a rule"

    rule_id = http_response.json["data"]["rule_id"]

    serialized_response = response_factory.serialize_response(response=response_200)

    http_response = client.post(
        urljoin(configuration_endpoint, "response/{0}".format(rule_id)),
        json=serialized_response,
        )
    assert http_response.status_code == 200, "Can't set a response"

    assert client.open(base_endpoint, method=method).status_code == 200, "Wrong status code"


@pytest.mark.parametrize(argnames="method", argvalues=_METHODS)
def test_no_match(rule_factory, response_factory, response_200, method):
    """Check that MethodRule is not triggered for different methods.

    1. Prepare method rule in the rule factory.
    2. Configure application with the rule factory.
    3. Make a POST-request to create a method rule.
    4. Set a response for the rule.
    5. Make a request of different types.
    6. Check that the rule does not find a match for any of the requests.
    """
    base_endpoint = "/base/"
    configuration_endpoint = "/config/"

    preparator = RuleFactoryPreparator(rule_factory)
    preparator.prepare_method_rule(method_rule_class=MethodRule)

    application = configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        rule_factory=rule_factory,
        response_factory=response_factory,
        )

    rule = MethodRule(rule_type=RuleType.METHOD.name, method=method)
    serialized_rule = rule_factory.serialize_rule(rule=rule)

    client = application.test_client()

    http_response = client.post(urljoin(configuration_endpoint, "rules"), json=serialized_rule)

    assert http_response.status_code == 200, "Can't create a rule"

    rule_id = http_response.json["data"]["rule_id"]

    serialized_response = response_factory.serialize_response(response=response_200)

    http_response = client.post(
        urljoin(configuration_endpoint, "response/{0}".format(rule_id)),
        json=serialized_response,
        )
    assert http_response.status_code == 200, "Can't set a response"

    method_responses = [
        client.open(base_endpoint, method=wrong_method)
        for wrong_method in _METHODS if wrong_method != method
        ]
    assert all(method_response.status_code == 404 for method_response in method_responses), (
        "Match found for at least one of the other methods"
        )
