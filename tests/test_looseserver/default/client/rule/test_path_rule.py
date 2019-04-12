"""Test cases for PathRule."""

from urllib.parse import urljoin

from looseserver.default.common.constants import RuleType
from looseserver.default.common.configuration import RuleFactoryPreparator
from looseserver.default.client.rule import PathRule


def test_default_rule_type():
    """Check the default rule type of the path rule.

    1. Create a path rule without specifying its type.
    2. Check the rule type.
    """
    rule = PathRule(path="path")
    assert rule.rule_type == RuleType.PATH.name, "Wrong rule type"


def test_rule_representation():
    """Check the representation of the path rule.

    1. Create a path rule.
    2. Check result of the repr function.
    """
    rule = PathRule(path="test")
    assert repr(rule) == "PathRule(path='test')", "Wrong representation"


def test_creation(base_endpoint, client_rule_factory, configured_flask_client):
    """Check that PathRule can be created.

    1. Prepare path rule in the rule factory of the flask client.
    2. Create a path rule with the client.
    3. Check the created rule.
    """
    preparator = RuleFactoryPreparator(client_rule_factory)
    preparator.prepare_path_rule(path_rule_class=PathRule, base_url=base_endpoint)

    rule_spec = PathRule(path="path-rule")
    rule = configured_flask_client.create_rule(rule=rule_spec)

    assert rule.rule_id is not None, "Rule was not created"
    assert rule.path == urljoin(base_endpoint, rule_spec.path), "Wrong path"
