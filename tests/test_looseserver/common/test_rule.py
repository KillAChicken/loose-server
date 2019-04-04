"""Test cases for looseserver common rule entities."""

from collections import namedtuple

import pytest

from looseserver.common.rule import RuleFactory, RuleError, RuleParseError, RuleSerializeError


RuleClass = namedtuple("RuleClass", "rule_type parameters")


def test_parse_rule():
    """Check that registered parser is used by rule factory.

    1. Create rule factory.
    2. Register new rule type.
    3. Parse a rule.
    4. Check that the rule is successfully parsed.
    """
    rule_factory = RuleFactory()
    parser = lambda rule_type, rule_data: (rule_type, rule_data)

    rule_type = "Test"
    rule_factory.register_rule(rule_type=rule_type, parser=parser, serializer=None)

    rule_parameters = {
        "key": "value",
        }
    rule_data = {
        "rule_type": rule_type,
        "parameters": rule_parameters,
        }

    parsed_rule = rule_factory.parse_rule(data=rule_data)
    assert parsed_rule == (rule_type, rule_parameters), "Rule has not been parsed"


def test_parse_wrong_data_type():
    """Check that RuleParseError is raised on attempt to parse wrong data type.

    1. Create rule factory.
    2. Register new rule type.
    3. Try to parse a rule from an object that without __getitem__.
    4. Check that RuleParseError is raised.
    5. Check the message of the error.
    """
    rule_factory = RuleFactory()
    parser = lambda *args, **kwargs: None

    rule_factory.register_rule(rule_type="Test", parser=parser, serializer=None)

    with pytest.raises(RuleParseError) as exception_info:
        rule_factory.parse_rule(data=None)

    assert exception_info.value.args[0] == "Failed to parse rule type. Wrong data format", (
        "Wrong error message"
        )


def test_parse_data_without_type():
    """Check that RuleParseError is raised on attempt to parse dictionary without "rule_type" key.

    1. Create rule factory.
    2. Register new rule type.
    3. Try to parse a rule from a dictionary without "rule_type" key.
    4. Check that RuleParseError is raised.
    5. Check the message of the error.
    """
    rule_factory = RuleFactory()
    parser = lambda *args, **kwargs: None

    rule_factory.register_rule(rule_type="Test", parser=parser, serializer=None)

    with pytest.raises(RuleParseError) as exception_info:
        rule_factory.parse_rule(data={"parameters": {"key": "value"}})

    assert exception_info.value.args[0] == "Failed to parse rule. Type is not specified", (
        "Wrong error message"
        )


def test_parse_unknown_type():
    """Check that RuleParseError is raised on attempt to parse rule of unknown type.

    1. Create rule factory.
    2. Register new rule type.
    3. Try to parse a rule with unregistered type.
    4. Check that RuleParseError is raised.
    5. Check the message of the error.
    """
    rule_factory = RuleFactory()
    parser = lambda *args, **kwargs: None
    rule_factory.register_rule(rule_type="Test", parser=parser, serializer=None)

    rule_data = {
        "rule_type": "NonExistentType",
        "parameters": {},
        }

    with pytest.raises(RuleParseError) as exception_info:
        rule_factory.parse_rule(data=rule_data)

    assert exception_info.value.args[0] == "Failed to parse rule. Unknown type 'NonExistentType'", (
        "Wrong error message"
        )


def test_parse_data_without_parameters():
    """Check that RuleParseError is raised on attempt to parse dictionary without "parameters" key.

    1. Create rule factory.
    2. Register new rule type.
    3. Try to parse a rule from a dictionary without "parameters" key.
    4. Check that RuleParseError is raised.
    5. Check the message of the error.
    """
    rule_factory = RuleFactory()
    parser = lambda *args, **kwargs: None

    rule_type = "Test"
    rule_factory.register_rule(rule_type=rule_type, parser=parser, serializer=None)

    with pytest.raises(RuleParseError) as exception_info:
        rule_factory.parse_rule(data={"rule_type": rule_type})

    assert exception_info.value.args[0] == "Failed to parse rule. Parameters are not specified", (
        "Wrong error message"
        )


def test_parse_rule_with_error():
    """Check that RuleParseError is propagated from parsers.

    1. Create rule factory.
    2. Register a new rule type with a parser, raising RuleParseError.
    3. Try to parse a rule.
    4. Check that RuleParseError is raised.
    """
    rule_factory = RuleFactory()
    error = RuleParseError("TestError")
    def _parser(rule_type, rule_data):
        # pylint: disable=unused-argument
        raise error

    rule_type = "Test"
    rule_factory.register_rule(rule_type=rule_type, parser=_parser, serializer=None)

    rule_data = {
        "rule_type": rule_type,
        "parameters": {},
        }

    with pytest.raises(RuleParseError) as exception_info:
        rule_factory.parse_rule(data=rule_data)

    assert exception_info.value is error, "Wrong error is raised"


def test_parse_rule_with_unknown_error():
    """Check that RuleError is raised if unhandled exception is raised by a parser.

    1. Create rule factory.
    2. Register a new rule type with a parser, raising an error different from RuleParseError.
    3. Try to parse a rule.
    4. Check that RuleError is raised.
    """
    rule_factory = RuleFactory()
    error = ValueError("TestError")
    def _parser(rule_type, rule_data):
        # pylint: disable=unused-argument
        raise error

    rule_type = "Test"
    rule_factory.register_rule(rule_type=rule_type, parser=_parser, serializer=None)

    rule_data = {
        "rule_type": rule_type,
        "parameters": {},
        }

    with pytest.raises(RuleError) as exception_info:
        rule_factory.parse_rule(data=rule_data)

    actual_error = exception_info.value
    assert not isinstance(actual_error, RuleParseError), "Wrong type of the error"
    assert actual_error.args[0] == "Failed to create a rule", "Wrong error message"
    assert actual_error.__cause__ is error, "Wrong reason"


def test_serialize_rule():
    """Check that registered serializer is used by rule factory.

    1. Create rule factory.
    2. Register new rule type.
    3. Serialize a rule.
    4. Check that the rule is successfully serialized.
    """
    rule_factory = RuleFactory()
    def _serializer(rule_type, rule):
        return rule_type, rule

    rule_type = "Test"
    rule_factory.register_rule(rule_type=rule_type, parser=None, serializer=_serializer)
    rule = RuleClass(rule_type=rule_type, parameters={})

    expected_serialized_rule = {
        "rule_type": rule_type,
        "parameters": (
            rule_type,
            rule,
            ),
        }

    serialized_rule = rule_factory.serialize_rule(rule=rule)
    assert serialized_rule == expected_serialized_rule, "Rule has not been serialized"


def test_serialize_wrong_object():
    """Check that RuleSerializeError is raised on attempt to serialize object without rule_type.

    1. Create rule factory.
    2. Register new rule type.
    3. Try to serialize an object without rule_type attribute.
    4. Check that RuleSerializeError is raised.
    5. Check the message of the error.
    """
    rule_factory = RuleFactory()
    serializer = lambda *args, **kwargs: None

    rule_factory.register_rule(rule_type="Test", parser=None, serializer=serializer)

    with pytest.raises(RuleSerializeError) as exception_info:
        rule_factory.serialize_rule(rule=None)

    assert exception_info.value.args[0] == "Failed to obtain type of the rule", (
        "Wrong error message"
        )


def test_serialize_unknown_type():
    """Check that RuleSerializeError is raised on attempt to serialize rule of unknown type.

    1. Create rule factory.
    2. Register new rule type.
    3. Try to serialize a rule with unregistered type.
    4. Check that RuleSerializeError is raised.
    5. Check the message of the error.
    """
    rule_factory = RuleFactory()
    serializer = lambda *args, **kwargs: None
    rule_factory.register_rule(rule_type="Test", parser=None, serializer=serializer)

    rule = RuleClass(rule_type="NonExistentType", parameters={})

    with pytest.raises(RuleSerializeError) as exception_info:
        rule_factory.serialize_rule(rule=rule)

    expected_message = "Failed to serialize rule {0}. Unknown type 'NonExistentType'".format(rule)
    assert exception_info.value.args[0] == expected_message, "Wrong error message"


def test_serialize_rule_with_error():
    """Check that RuleSerializeError is propagated from serializers.

    1. Create rule factory.
    2. Register a new rule type with a serializer, raising RuleSerializeError
    3. Try to serialize a rule.
    4. Check that RuleSerializeError is raised.
    """
    rule_factory = RuleFactory()
    error = RuleSerializeError("TestError")
    def _serializer(rule_type, rule):
        # pylint: disable=unused-argument
        raise error

    rule_type = "Test"
    rule_factory.register_rule(rule_type=rule_type, parser=None, serializer=_serializer)

    rule = RuleClass(rule_type=rule_type, parameters={})

    with pytest.raises(RuleSerializeError) as exception_info:
        rule_factory.serialize_rule(rule=rule)

    assert exception_info.value is error, "Wrong error is raised"


def test_serialize_rule_with_unknown_error():
    """Check that RuleError is raised if unhandled exception is raised by a serializer.

    1. Create rule factory.
    2. Register a new rule type with a serialier,
       raising an error different from RuleSerializeError.
    3. Try to serialize a rule.
    4. Check that RuleError is raised.
    """
    rule_factory = RuleFactory()
    error = ValueError("TestError")
    def _serializer(rule_type, rule):
        # pylint: disable=unused-argument
        raise error

    rule_type = "Test"
    rule_factory.register_rule(rule_type=rule_type, parser=None, serializer=_serializer)

    rule = RuleClass(rule_type=rule_type, parameters={})

    with pytest.raises(RuleError) as exception_info:
        rule_factory.serialize_rule(rule=rule)

    actual_error = exception_info.value
    assert not isinstance(actual_error, RuleSerializeError), "Wrong type of the error"
    assert actual_error.args[0] == "Failed to serialize a rule", "Wrong error message"
    assert actual_error.__cause__ is error, "Wrong reason"
