"""Test cases to check the configuration for method rules."""

from collections import namedtuple

import pytest

from looseserver.common.rule import RuleParseError, RuleSerializeError
from looseserver.default.common.constants import RuleType
from looseserver.default.common.configuration import RuleFactoryPreparator


_MethodRule = namedtuple("MethodRule", "method rule_type")


def test_prepare_method_rule(server_rule_factory):
    """Check that method rule can be serialized.

    1. Create preparator for a rule factory.
    2. Prepare method rule.
    3. Serialize new rule.
    4. Parse serialized data.
    5. Check parsed rule.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_method_rule(method_rule_class=_MethodRule)

    rule = _MethodRule(method="PUT", rule_type=RuleType.METHOD.name)
    serialized_rule = server_rule_factory.serialize_rule(rule=rule)

    assert serialized_rule["parameters"] == {"method": rule.method}, "Incorrect serialization"

    parsed_rule = server_rule_factory.parse_rule(data=serialized_rule)

    assert isinstance(parsed_rule, _MethodRule), "Wrong type of the rule"
    assert parsed_rule.rule_type == RuleType.METHOD.name, "Wrong rule type"
    assert parsed_rule.method == rule.method, "Wrong method"


def test_parse_missing_method(server_rule_factory):
    """Check that RuleParseError is raised if method is missing.

    1. Create preparator for a rule factory.
    2. Prepare method rule.
    3. Try to parse data without "method" key.
    4. Check that RuleParseError is raised.
    5. Check the error.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_method_rule(method_rule_class=_MethodRule)

    rule = _MethodRule(rule_type=RuleType.METHOD.name, method="POST")
    serialized_rule = server_rule_factory.serialize_rule(rule=rule)
    serialized_rule["parameters"].pop("method")

    with pytest.raises(RuleParseError) as exception_info:
        server_rule_factory.parse_rule(serialized_rule)

    expected_message = "Rule parameters must be a dictionary with 'method' key"
    assert exception_info.value.args[0] == expected_message, "Wrong error message"


def test_parse_wrong_parameters_type(server_rule_factory):
    """Check that RuleParseError is raised if parameters are of a wrong type.

    1. Create preparator for a rule factory.
    2. Prepare method rule.
    3. Try to parse data with string parameters.
    4. Check that RuleParseError is raised.
    5. Check the error.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_method_rule(method_rule_class=_MethodRule)

    rule = _MethodRule(rule_type=RuleType.METHOD.name, method="DELETE")
    serialized_rule = server_rule_factory.serialize_rule(rule=rule)
    serialized_rule["parameters"] = ""

    with pytest.raises(RuleParseError) as exception_info:
        server_rule_factory.parse_rule(serialized_rule)

    expected_message = "Rule parameters must be a dictionary with 'method' key"
    assert exception_info.value.args[0] == expected_message, "Wrong error message"


def test_serialize_missing_method(server_rule_factory):
    """Check that RuleSerializeError is raised if rule class does not have method attribute.

    1. Create preparator for a rule factory.
    2. Prepare method rule.
    3. Try to serialize rule without method attribute.
    4. Check that RuleSerializeError is raised.
    5. Check the error.
    """
    class _WrongRule:
        # pylint: disable=too-few-public-methods
        def __init__(self, method, rule_type):
            # pylint: disable=unused-argument
            self.rule_type = rule_type

    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_method_rule(method_rule_class=_WrongRule)

    rule = _WrongRule(method="GET", rule_type=RuleType.METHOD.name)

    with pytest.raises(RuleSerializeError) as exception_info:
        server_rule_factory.serialize_rule(rule=rule)

    assert exception_info.value.args[0] == "Method rule must have method attribute", (
        "Wrong error message"
        )
