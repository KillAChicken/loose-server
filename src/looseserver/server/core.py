"""Core module to manage dynamically configured routes."""

from collections import OrderedDict
from uuid import uuid4
import logging

from flask import request, abort


class Manager:
    """Class to manage routes."""

    def __init__(self, base):
        self._base = base
        self._rules = OrderedDict()
        self._responses = {}

    @property
    def base(self):
        """Base path for endpoints."""
        return self._base

    def view(self, path=""):
        # pylint: disable=unused-argument
        """View function for configured path.

        :param path: path relative to the routes endpoint.
        """
        logger = logging.getLogger(__name__)
        for rule_id, rule in self._rules.items():
            try:
                match_found = rule.is_match_found(request)
            except Exception:  # pylint: disable=broad-except
                logger.exception("Error occured on attempt to find a match by %s", rule)
                continue

            if match_found:
                response = self._responses.get(rule_id)
                if response is None:
                    continue
                else:
                    try:
                        return response.build_response(request=request, rule=rule)
                    except Exception:  # pylint: disable=broad-except
                        logger.exception(
                            "Error occured on attempt to build response by %s",
                            response,
                            )
                        continue

        return abort(404)

    def get_rule(self, rule_id):
        """Get a rule by its ID.

        :param rule_id: ID of the rule.
        :returns: instance of :class:`Rule <looseserver.server.rule._AbstractRule>`.
        :raises: :class:KeyError if there is no rule with the specified ID.
        """
        logger = logging.getLogger(__name__)
        logger.debug("Try to get rule by ID '%s'", rule_id)
        rule = self._rules.get(rule_id)
        if rule is None:
            raise KeyError("Failed to find a rule with ID: '{0}'".format(rule_id))

        logger.info("Successfully obtained rule by ID '%s'", rule_id)
        return rule

    def get_rules_order(self):
        """Get order of the rules.

        :returns: tuple with rule IDs.
        """
        return tuple(self._rules.keys())

    def add_rule(self, rule):
        """Add a rule to match the request.

        :param rule: instance of :class:`Rule <looseserver.server.rule._AbstractRule>`.
        :returns: ID of the created rule.
        """
        logger = logging.getLogger(__name__)
        logger.debug("Try to add rule %s", rule)

        rules = self._rules

        rule_id = str(uuid4())
        while rule_id in rules:
            rule_id = str(uuid4())

        rules[rule_id] = rule

        logger.info("Rule %s has been added with ID %s", rule, rule_id)
        return rule_id

    def remove_rule(self, rule_id):
        """Remove rule.

        :param rule_id: ID of the rule.
        """
        logger = logging.getLogger(__name__)
        logger.debug("Try to remove rule with ID '%s'", rule_id)

        self._rules.pop(rule_id, None)
        self._responses.pop(rule_id, None)

        logger.info("Rule with ID %s has been removed", rule_id)

    def get_response(self, rule_id):
        """Get a response for the rule.

        :param rule_id: ID of the rule.
        :returns: instance of :class:`Response <looseserver.server.response._AbstractResponse>`.
        :raises: :class:KeyError if there is no rule with the specified ID or
            response has not been set yet.
        """
        logger = logging.getLogger(__name__)
        logger.debug("Try to get response for the rule with ID '%s'", rule_id)
        if rule_id not in self._rules:
            raise KeyError("Failed to find a rule with ID: '{0}'".format(rule_id))

        response = self._responses.get(rule_id, None)
        if response is None:
            raise KeyError("Response has not been set for the rule with ID: '{0}'".format(rule_id))

        logger.info("Successfully obtained response for the rule with ID '%s'", rule_id)
        return response

    def set_response(self, rule_id, response):
        """Set a response for the rule.

        :param rule_id: ID of the rule.
        :param response: instance of
            :class:`Response <looseserver.server.response._AbstractResponse>`.
        :raises: :class:KeyError if there is no rule with the specified ID.
        """
        logger = logging.getLogger(__name__)
        logger.debug("Try to set response %s for the rule with ID %s", response, rule_id)

        if rule_id not in self._rules:
            raise KeyError("Failed to find a rule with ID: '{0}'".format(rule_id))

        self._responses[rule_id] = response

        logger.info("Response %s has been set for the rule with ID %s", response, rule_id)
