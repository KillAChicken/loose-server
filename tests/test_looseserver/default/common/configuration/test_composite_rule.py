"""Test cases to check the configuration for composite rules."""

from collections import namedtuple

import pytest

from looseserver.common.rule import RuleParseError, RuleSerializeError
from looseserver.default.common.constants import RuleType
from looseserver.default.common.configuration import RuleFactoryPreparator


_MethodRule = namedtuple("_MethodRule", "method rule_type")
_CompositeRule = namedtuple("_CompositeRule", "children rule_type")


@pytest.mark.parametrize(
    argnames="number_of_children",
    argvalues=[2, 0, 1],
    ids=["Several children", "Without children", "Single children"],
    )
def test_prepare_composite_rule(rule_factory, number_of_children):
    """Check that composite rule can be serialized.

    1. Create preparator for a rule factory.
    2. Prepare method and composite rules.
    3. Serialize new composite rule.
    4. Parse serialized data.
    5. Check parsed rule.
    """
    preparator = RuleFactoryPreparator(rule_factory)
    preparator.prepare_method_rule(method_rule_class=_MethodRule)
    preparator.prepare_composite_rule(composite_rule_class=_CompositeRule)

    children = [
        _MethodRule(rule_type=RuleType.METHOD.name, method=str(index))
        for index in range(number_of_children)
        ]
    rule = _CompositeRule(children=children, rule_type=RuleType.COMPOSITE.name)
    serialized_rule = rule_factory.serialize_rule(rule=rule)

    expected_serialized_children = [rule_factory.serialize_rule(rule=child) for child in children]

    assert serialized_rule["parameters"] == {"children": expected_serialized_children}, (
        "Incorrect serialization"
        )

    parsed_rule = rule_factory.parse_rule(data=serialized_rule)

    assert isinstance(parsed_rule, _CompositeRule), "Wrong type of the rule"
    assert parsed_rule.rule_type == RuleType.COMPOSITE.name, "Wrong rule type"
    assert len(parsed_rule.children) == number_of_children, "Wrong number of children"
    assert all(
        child == expected_child
        for child, expected_child in zip(parsed_rule.children, children)
        ), "Wrong children"


def test_parse_missing_children(rule_factory):
    """Check that RuleParseError is raised if children are missing.

    1. Create preparator for a rule factory.
    2. Prepare composite rule.
    3. Try to parse data without "children" key.
    4. Check that RuleParseError is raised.
    5. Check the error.
    """
    preparator = RuleFactoryPreparator(rule_factory)
    preparator.prepare_composite_rule(composite_rule_class=_CompositeRule)

    rule = _CompositeRule(rule_type=RuleType.COMPOSITE.name, children=())
    serialized_rule = rule_factory.serialize_rule(rule=rule)
    serialized_rule["parameters"].pop("children")

    with pytest.raises(RuleParseError) as exception_info:
        rule_factory.parse_rule(serialized_rule)

    expected_message = "Rule parameters must be a dictionary with 'children' key"
    assert exception_info.value.args[0] == expected_message, "Wrong error message"


def test_parse_wrong_parameters_type(rule_factory):
    """Check that RuleParseError is raised if parameters are of a wrong type.

    1. Create preparator for a rule factory.
    2. Prepare composite rule.
    3. Try to parse data with string parameters.
    4. Check that RuleParseError is raised.
    5. Check the error.
    """
    preparator = RuleFactoryPreparator(rule_factory)
    preparator.prepare_composite_rule(composite_rule_class=_CompositeRule)

    rule = _CompositeRule(rule_type=RuleType.COMPOSITE.name, children=())
    serialized_rule = rule_factory.serialize_rule(rule=rule)
    serialized_rule["parameters"] = ""

    with pytest.raises(RuleParseError) as exception_info:
        rule_factory.parse_rule(serialized_rule)

    expected_message = "Rule parameters must be a dictionary with 'children' key"
    assert exception_info.value.args[0] == expected_message, "Wrong error message"


def test_serialize_missing_children(rule_factory):
    """Check that RuleSerializeError is raised if rule class does not have children attribute.

    1. Create preparator for a rule factory.
    2. Prepare composite rule.
    3. Try to serialize rule without children attribute.
    4. Check that RuleSerializeError is raised.
    5. Check the error.
    """
    class _WrongRule:
        # pylint: disable=too-few-public-methods
        def __init__(self, children, rule_type):
            # pylint: disable=unused-argument
            self.rule_type = rule_type

    preparator = RuleFactoryPreparator(rule_factory)
    preparator.prepare_composite_rule(composite_rule_class=_WrongRule)

    rule = _WrongRule(children=(), rule_type=RuleType.COMPOSITE.name)

    with pytest.raises(RuleSerializeError) as exception_info:
        rule_factory.serialize_rule(rule=rule)

    assert exception_info.value.args[0] == "Composite rule must have children attribute", (
        "Wrong error message"
        )
