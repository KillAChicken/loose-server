"""Test cases for looseserver server rules."""

from looseserver.server.rule import ServerRule


def test_rule_type():
    """Check that rule type can be obtained.

    1. Create class for a rule.
    2. Create instance of the class.
    3. Check the type of the rule.
    """
    class Rule(ServerRule):
        """Test rule."""
        def is_match_found(self, request):
            """Test implementation."""

    rule = Rule(rule_type="test")
    assert rule.rule_type == "test", "Wrong rule type"
