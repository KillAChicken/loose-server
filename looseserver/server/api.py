"""Module with api resources."""

import logging
from collections import OrderedDict

from flask import request
from flask_restful import Resource

from looseserver.common.api import DEFAULT_VERSION, ResponseStatus, APIError
from looseserver.common.rule import RuleError, RuleParseError
from looseserver.common.response import ResponseError, ResponseParseError


class RulesManager(Resource):
    """API resource to manage rules."""
    def __init__(self, manager, rule_factory):
        self._manager = manager
        self._rule_factory = rule_factory

    def post(self):
        """Create a new rule."""
        logger = logging.getLogger(__name__)
        request_data = request.get_json(silent=True)
        if request_data is None:
            message = "Failed to parse JSON data from the request"
            logger.error(message)
            return build_response(error=APIError(message)), 400

        logger.debug("Try to create new rule")
        try:
            rule = self._rule_factory.parse_rule(data=request_data)
        except RuleParseError as error:
            message = "Failed to create a rule for specified parameters. Error: '{0}'".format(error)
            logger.exception(message)
            return build_response(error=APIError(message)), 400
        except RuleError as error:
            message = "Exception has been raised during rule creation"
            logger.exception(message)
            return build_response(error=APIError(message)), 500

        rule_id = self._manager.add_rule(rule)
        logger.debug("Rule has been successfully created")

        try:
            rule_data = self._rule_factory.serialize_rule(rule)
        except RuleError:
            self._manager.remove_rule(rule_id=rule_id)
            logger.debug("Rule has been removed because of a serialization error")
            message = "Rule may be created, but can't be serialized"
            return build_response(error=APIError(message)), 500

        logger.info("Successfully handled request to create a rule")

        response_data = {"rule_id": rule_id}
        response_data.update(rule_data)
        return build_response(data=response_data)


class Rule(Resource):
    """API resource to manage single rule."""
    def __init__(self, manager, rule_factory):
        self._manager = manager
        self._rule_factory = rule_factory

    def get(self, rule_id):
        """Get rule by its ID."""
        logger = logging.getLogger(__name__)
        logger.debug("Try to get rule %s", rule_id)
        try:
            rule = self._manager.get_rule(rule_id=rule_id)
        except KeyError:
            message = "Failed to find rule with ID '{0}'".format(rule_id)
            logger.error(message)
            return build_response(error=APIError(message)), 404

        try:
            rule_data = self._rule_factory.serialize_rule(rule)
        except RuleError:
            message = "Exception has been raised during serialization of the rule"
            logger.exception(message)
            return build_response(error=APIError(message)), 500

        logger.info("Rule %s has been successfully obtained", rule_id)
        response_data = {"rule_id": rule_id}
        response_data.update(rule_data)
        return build_response(data=response_data)


class Response(Resource):
    """API resource to manage rule responses."""
    def __init__(self, manager, response_factory):
        self._manager = manager
        self._response_factory = response_factory

    def post(self, rule_id):
        """Create a new response for the rule."""
        logger = logging.getLogger(__name__)
        request_data = request.get_json(silent=True)
        if request_data is None:
            message = "Failed to parse JSON data from the request"
            logger.error(message)
            return build_response(error=APIError(message)), 400

        logger.debug("Try to create new response for the rule with ID %s", rule_id)
        try:
            response = self._response_factory.parse_response(data=request_data)
        except ResponseParseError as error:
            message = "Failed to create a response for specified parameters. Error: '{0}'".format(
                error,
                )
            logger.exception(message)
            return build_response(error=APIError(message)), 400
        except ResponseError as error:
            message = "Exception has been raised during response creation"
            logger.exception(message)
            return build_response(error=APIError(message)), 500

        try:
            response_data = self._response_factory.serialize_response(response)
        except ResponseError:
            message = "Response can't be serialized"
            return build_response(error=APIError(message)), 500

        try:
            self._manager.set_response(rule_id=rule_id, response=response)
        except KeyError:
            message = "Failed to create a response: Rule does not exist"
            logger.exception(message)
            return build_response(error=APIError(message)), 400

        logger.debug("Response has been successfully created for the rule with ID %s", rule_id)

        logger.info(
            "Successfully handled request to set a response for the rule with ID %s",
            rule_id,
            )

        return build_response(data=response_data)

    def get(self, rule_id):
        """Get response by rule ID."""
        logger = logging.getLogger(__name__)
        logger.debug("Try to get the response for the rule with ID '%s'", rule_id)
        try:
            response = self._manager.get_response(rule_id=rule_id)
        except KeyError:
            message = "Failed to get response for the rule '{0}'".format(rule_id)
            logger.exception(message)
            return build_response(error=APIError(message)), 404

        try:
            response_data = self._response_factory.serialize_response(response)
        except ResponseError:
            message = "Response can't be serialized"
            logger.exception(message)
            return build_response(error=APIError(message)), 500

        logger.info("Response for the rule with ID %s has been successfully obtained", rule_id)
        return build_response(data=response_data)


def build_response(data=None, error=None, version=DEFAULT_VERSION):
    """Build a response.

    :param data: JSON serializable object to include into the response.
    :param error: instance of :class:`APIError <looseserver.common.api.APIError>`.
    :param version: version of API.
    :returns: JSON serializable object with response.
    """
    if error:
        status = ResponseStatus.FAILURE
    else:
        status = ResponseStatus.SUCCESS

    response_json = OrderedDict((
        ("version", version),
        ("status", status.name),
        ))

    if error:
        response_json["error"] = {
            "description": error.description,
            }

    if data is not None:
        response_json["data"] = data

    return response_json
