"""Test cases for PathRule."""

from urllib.parse import urljoin

import pytest

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
def test_match_found(
        base_endpoint,
        server_rule_factory,
        configured_application_client,
        apply_rule,
        path,
    ):
    """Check that PathRule is triggered for the specified path.

    1. Prepare path rule in the rule factory.
    2. Create a path rule and set successful response for it.
    3. Make a request to the specified path.
    4. Check that the rule finds a match.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_path_rule(path_rule_class=PathRule, base_url=base_endpoint)

    rule = PathRule(rule_type=RuleType.PATH.name, path=path)
    apply_rule(rule)

    http_response = configured_application_client.get(urljoin(base_endpoint, path))
    assert http_response.status_code == 200, "Wrong status code"


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
def test_no_match(
        base_endpoint,
        server_rule_factory,
        configured_application_client,
        apply_rule,
        path,
        unmanaged_path,
    ):
    # pylint: disable=too-many-arguments
    """Check that PathRule is not triggered for different paths.

    1. Prepare path rule in the rule factory.
    2. Create a path rule and set successful response for it.
    3. Make a request to a different path.
    4. Check that the rule does not find a match.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_path_rule(path_rule_class=PathRule, base_url=base_endpoint)

    rule = PathRule(rule_type=RuleType.PATH.name, path=path)
    apply_rule(rule)

    http_response = configured_application_client.get(urljoin(base_endpoint, unmanaged_path))
    assert http_response.status_code == 404, "Wrong status code"
