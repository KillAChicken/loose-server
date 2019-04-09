"""Test cases for looseserver client rules."""

from looseserver.client.rule import ClientRule


def test_rule_type():
    """Check that rule type can be obtained.

    1. Create instance of the class.
    2. Check the type of the rule.
    """
    rule = ClientRule(rule_type="test")
    assert rule.rule_type == "test", "Wrong rule type"
