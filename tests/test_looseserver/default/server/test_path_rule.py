"""Test cases for PathRule."""

from urllib.parse import urljoin

import pytest

from looseserver.server.application import configure_application
from looseserver.default.common.constants import RuleType
from looseserver.default.common.configuration import RuleFactoryPreparator
from looseserver.default.server.rule import PathRule


def test_rule_representation():
    """Check the representation of the path rule.

    1. Create a path rule.
    2. Check result of the repr function.
    """
    rule = PathRule(path="test", rule_type=RuleType.PATH.name)
    assert repr(rule) == "PathRule(path='test')", "Wrong representation"


@pytest.mark.parametrize(
    argnames="path",
    argvalues=[
        "",
        "child",
        "child/grandchild",
        ],
    ids=[
        "base",
        "child",
        "grandchild",
        ]
    )
def test_match_found(rule_factory, response_factory, response_200, path):
    """Check that PathRule is triggered for the specified path.

    1. Prepare path rule in the rule factory.
    2. Configure application with the rule factory.
    3. Make a POST-request to create a path rule.
    4. Set a response for the rule.
    5. Make a request to the specified path.
    6. Check that the rule finds a match.
    """
    base_endpoint = "/base/"
    configuration_endpoint = "/config/"

    preparator = RuleFactoryPreparator(rule_factory)
    preparator.prepare_path_rule(path_rule_class=PathRule, base_url=base_endpoint)

    application = configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        rule_factory=rule_factory,
        response_factory=response_factory,
        )

    rule = PathRule(rule_type=RuleType.PATH.name, path=path)
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

    assert client.get(urljoin(base_endpoint, path)).status_code == 200, "Wrong status code"


@pytest.mark.parametrize(
    argnames="path,unmanaged_path",
    argvalues=[
        ("parent", "parent/child"),
        ("parent/child", "parent"),
        ("prefix", "prefix-postfix"),
        ],
    ids=[
        "Nested path",
        "Parent path",
        "Substring",
        ],
    )
def test_no_match(rule_factory, response_factory, response_200, path, unmanaged_path):
    """Check that PathRule is not triggered for different paths.

    1. Prepare path rule in the rule factory.
    2. Configure application with the rule factory.
    3. Make a POST-request to create a path rule.
    4. Set a response for the rule.
    5. Make a request to a different path.
    6. Check that the rule does not find a match.
    """
    base_endpoint = "/base/"
    configuration_endpoint = "/config/"

    preparator = RuleFactoryPreparator(rule_factory)
    preparator.prepare_path_rule(path_rule_class=PathRule, base_url=base_endpoint)

    application = configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        rule_factory=rule_factory,
        response_factory=response_factory,
        )

    rule = PathRule(rule_type=RuleType.PATH.name, path=path)
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

    assert client.get(urljoin(base_endpoint, unmanaged_path)).status_code == 404, (
        "Wrong status code"
        )
