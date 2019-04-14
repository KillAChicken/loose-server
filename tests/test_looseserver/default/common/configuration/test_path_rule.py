"""Test cases to check the configuration for path rules."""

from collections import namedtuple
from urllib.parse import urljoin

import pytest

from looseserver.common.rule import RuleParseError, RuleSerializeError
from looseserver.default.common.constants import RuleType
from looseserver.default.common.configuration import RuleFactoryPreparator


_PathRule = namedtuple("_PathRule", "path rule_type")


def test_prepare_path_rule(server_rule_factory):
    """Check that path rule can be serialized.

    1. Create preparator for a rule factory.
    2. Prepare path rule.
    3. Serialize new rule.
    4. Parse serialized data.
    5. Check parsed rule.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    base_url = "/base/"
    preparator.prepare_path_rule(path_rule_class=_PathRule, base_url=base_url)

    path = "test-path"
    rule = _PathRule(path=path, rule_type=RuleType.PATH.name)
    serialized_rule = server_rule_factory.serialize_rule(rule=rule)

    assert serialized_rule["parameters"] == {"path": rule.path}, "Incorrect serialization"

    parsed_rule = server_rule_factory.parse_rule(data=serialized_rule)

    assert isinstance(parsed_rule, _PathRule), "Wrong type of the rule"
    assert parsed_rule.rule_type == RuleType.PATH.name, "Wrong rule type"


def test_path_with_base_url(server_rule_factory):
    """Check that parser adds base url if it was specified.

    1. Create preparator for a rule factory.
    2. Prepare path rule with custom base url.
    3. Serialize new rule.
    4. Parse serialized data.
    5. Check parsed rule path.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    base_url = "/base/"
    preparator.prepare_path_rule(path_rule_class=_PathRule, base_url=base_url)

    path = "test-path"
    rule = _PathRule(path=path, rule_type=RuleType.PATH.name)
    serialized_rule = server_rule_factory.serialize_rule(rule=rule)
    parsed_rule = server_rule_factory.parse_rule(data=serialized_rule)
    assert parsed_rule.path == urljoin(base_url, path), "Wrong path"


def test_path_without_base_url(server_rule_factory):
    """Check that parser does not add base url if it was not specified.

    1. Create preparator for a rule factory.
    2. Prepare path rule without specifying base url.
    3. Serialize new rule.
    4. Parse serialized data.
    5. Check parsed rule path.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_path_rule(path_rule_class=_PathRule)

    rule = _PathRule(path="path", rule_type=RuleType.PATH.name)
    serialized_rule = server_rule_factory.serialize_rule(rule=rule)
    parsed_rule = server_rule_factory.parse_rule(data=serialized_rule)
    assert parsed_rule.path == rule.path, "Wrong path"


def test_parse_missing_path(server_rule_factory):
    """Check that RuleParseError is raised if path is missing.

    1. Create preparator for a rule factory.
    2. Prepare path rule.
    3. Try to parse data without "path" key.
    4. Check that RuleParseError is raised.
    5. Check the error.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_path_rule(path_rule_class=_PathRule, base_url="/")

    rule = _PathRule(rule_type=RuleType.PATH.name, path="test")
    serialized_rule = server_rule_factory.serialize_rule(rule=rule)
    serialized_rule["parameters"].pop("path")

    with pytest.raises(RuleParseError) as exception_info:
        server_rule_factory.parse_rule(serialized_rule)

    assert exception_info.value.args[0] == "Rule parameters must be a dictionary with 'path' key", (
        "Wrong error message"
        )


def test_parse_wrong_parameters_type(server_rule_factory):
    """Check that RuleParseError is raised if parameters are of a wrong type.

    1. Create preparator for a rule factory.
    2. Prepare path rule.
    3. Try to parse data with string parameters.
    4. Check that RuleParseError is raised.
    5. Check the error.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_path_rule(path_rule_class=_PathRule, base_url="/")

    rule = _PathRule(rule_type=RuleType.PATH.name, path="test")
    serialized_rule = server_rule_factory.serialize_rule(rule=rule)
    serialized_rule["parameters"] = ""

    with pytest.raises(RuleParseError) as exception_info:
        server_rule_factory.parse_rule(serialized_rule)

    assert exception_info.value.args[0] == "Rule parameters must be a dictionary with 'path' key", (
        "Wrong error message"
        )


def test_serialize_missing_path(server_rule_factory):
    """Check that RuleSerializeError is raised if rule class does not have path attribute.

    1. Create preparator for a rule factory.
    2. Prepare path rule.
    3. Try to serialize rule without path attribute.
    4. Check that RuleSerializeError is raised.
    5. Check the error.
    """
    class _WrongRule:
        # pylint: disable=too-few-public-methods
        def __init__(self, path, rule_type):
            # pylint: disable=unused-argument
            self.rule_type = rule_type

    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_path_rule(path_rule_class=_WrongRule, base_url="/")

    rule = _WrongRule(path="/", rule_type=RuleType.PATH.name)

    with pytest.raises(RuleSerializeError) as exception_info:
        server_rule_factory.serialize_rule(rule=rule)

    assert exception_info.value.args[0] == "Path rule must have path attribute", (
        "Wrong error message"
        )
