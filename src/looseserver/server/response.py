"""Module with responses."""

from abc import ABC, abstractmethod


class ServerResponse(ABC):
    """Class to manage a response by the server."""

    def __init__(self, response_type):
        self._type = response_type

    @property
    def response_type(self):
        """Type of the response."""
        return self._type

    @abstractmethod
    def build_response(self, request, rule):
        """Build a response for the request.

        Returned value must be acceptable by the flask framework.

        :param request: instance of :class:flask.Request.
        :param rule: instance of :class:`Rule <looseserver.server.rule._AbstractRule>`.
        """
