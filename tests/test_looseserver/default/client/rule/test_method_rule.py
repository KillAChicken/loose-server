"""Test cases for MethodRule."""

from looseserver.default.common.constants import RuleType
from looseserver.default.common.configuration import RuleFactoryPreparator
from looseserver.default.client.rule import MethodRule


def test_default_rule_type():
    """Check the default rule type of the method rule.

    1. Create a method rule without specifying its type.
    2. Check the rule type.
    """
    rule = MethodRule(method="GET")
    assert rule.rule_type == RuleType.METHOD.name, "Wrong rule type"


def test_rule_representation():
    """Check the representation of the method rule.

    1. Create a method rule.
    2. Check result of the repr function.
    """
    rule = MethodRule(method="POST")
    assert repr(rule) == "MethodRule(method='POST')", "Wrong representation"


def test_creation(client_rule_factory, configured_flask_client):
    """Check that MethodRule can be created.

    1. Prepare method rule in the rule factory of the flask client.
    2. Create a method rule with the client.
    3. Check the created rule.
    """
    preparator = RuleFactoryPreparator(client_rule_factory)
    preparator.prepare_method_rule(method_rule_class=MethodRule)

    rule_spec = MethodRule(method="PUT")
    rule = configured_flask_client.create_rule(rule=rule_spec)

    assert rule.rule_id is not None, "Rule was not created"
    assert rule.method == rule_spec.method, "Wrong method"
