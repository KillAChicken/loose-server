"""Module with common rule entities."""

import logging


class RuleError(Exception):
    """Exception raised due to an error in rule processing (creation, handling, etc.)."""


class RuleParseError(RuleError):
    """Exception raised in case when a rule can't be created from the provided data."""


class RuleSerializeError(RuleError):
    """Exception raised in case when a rule can't be serialized."""


class RuleFactory:
    """Factory to register and create different types of rules."""

    def __init__(self):
        self._parsers = {}
        self._serializers = {}

    def register_rule(self, rule_type, parser, serializer):
        """Register new rule type.

        :param rule_type: string for rule type.
        :param parser: callable that converts JSON data into a rule object.
        :param serializer: callable that converts a rule into JSON data.
        """
        self._parsers[rule_type] = parser
        self._serializers[rule_type] = serializer
        logging.getLogger(__name__).info("Rule type '%s' has been registered", rule_type)

    def parse_rule(self, data):
        """Create a rule from data.

        :param data: data with rule information.
        :returns: new rule.
        :raises: :class:`RuleParseError`, if rule_type has not been registered or data is invalid.
        :raises: :class:`RuleError` if exception is raised during creation of the rule.
        """
        logger = logging.getLogger(__name__)
        logger.debug("Try to parse a rule")
        try:
            rule_type = data["rule_type"]
        except TypeError as error:
            raise RuleParseError("Failed to parse rule type. Wrong data format") from error
        except KeyError as error:
            raise RuleParseError("Failed to parse rule. Type is not specified") from error

        rule_parser = self._parsers.get(rule_type)
        if rule_parser is None:
            raise RuleParseError("Failed to parse rule. Unknown type '{0}'".format(rule_type))
        logger.debug("Rule parser for type '%s' has been obtained", rule_type)

        try:
            parameters = data["parameters"]
        except KeyError as error:
            raise RuleParseError("Failed to parse rule. Parameters are not specified") from error

        try:
            rule = rule_parser(rule_type, parameters)
        except RuleParseError:
            logger.exception("Invalid data have been specified for rule of type '%s'", rule_type)
            raise
        except Exception as error:
            logger.exception("Failed to create a rule of type '%s'", rule_type)
            raise RuleError("Failed to create a rule") from error
        else:
            logger.info("Successfully parsed rule %s", rule)

        return rule

    def serialize_rule(self, rule):
        """Create a dictionary from a rule.

        :param rule: rule to dump.
        :returns: dictionary with parameters of the rule.
        :raises: :class:`RuleSerializeError`, if rule does not have type, its type has not been
            registered or rule has unserializable data.
        :raises: :class:`RuleError` if exception is raised during serialization of the rule.
        """
        logger = logging.getLogger(__name__)
        logger.debug("Try to serialize rule %s", rule)

        try:
            rule_type = rule.rule_type
        except AttributeError as error:
            raise RuleSerializeError("Failed to obtain type of the rule") from error

        rule_serializer = self._serializers.get(rule_type)
        if rule_serializer is None:
            message = "Failed to serialize rule {rule}. Unknown type '{rule_type}'".format(
                rule=rule,
                rule_type=rule_type,
                )
            raise RuleSerializeError(message)

        logger.debug("Rule serializer for type '%s' has been obtained", rule_type)

        try:
            rule_parameters = rule_serializer(rule_type, rule)
        except RuleSerializeError:
            logger.exception("Rule %s can't be serialized", rule)
            raise
        except Exception as error:
            logger.exception("Failed to serialize rule %s", rule)
            raise RuleError("Failed to serialize a rule") from error
        else:
            logger.info("Rule of type '%s' has been successfully serialized", rule_type)

        return {
            "rule_type": rule_type,
            "parameters": rule_parameters,
            }
