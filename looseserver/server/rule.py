"""Module to work with server rules."""

from abc import ABC, abstractmethod


class ServerRule(ABC):
    """Class for abstract rule."""

    def __init__(self, rule_type):
        self._type = rule_type

    @property
    def rule_type(self):
        """Type of the rule."""
        return self._type

    @abstractmethod
    def is_match_found(self, request):
        """Check if a match for the rule is found in the request.

        :param request: instance of :class:flask.Request.
        :returns: boolean if match is found.
        """
