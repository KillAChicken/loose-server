"""Default server responses."""

import logging
from copy import copy

import flask

from looseserver.server.response import ServerResponse
from looseserver.common.response import ResponseFactory
from looseserver.default.common.configuration import ResponseFactoryPreparator


class FixedResponse(ServerResponse):
    """Class for fixed responses."""

    def __init__(self, response_type, body="", status=200, headers=()):
        super(FixedResponse, self).__init__(response_type=response_type)
        self._body = body
        self._status = status
        self._headers = {}
        self._headers.update(headers)

    @property
    def body(self):
        """Body of the response."""
        return self._body

    @property
    def status(self):
        """Status of the response."""
        return self._status

    @property
    def headers(self):
        """Headers of the response."""
        return copy(self._headers)

    def build_response(self, request, rule):
        # pylint: disable=unused-argument
        """Build a response.

        :param request: instance of :class:flask.Request. Ignored.
        :param rule: instance of :class:`Rule <looseserver.server.rule._AbstractRule>`. Ignored.
        :returns: instance of :class:flask.Response.
        """
        logging.getLogger(__name__).debug("Build fixed response")
        return flask.Response(response=self._body, status=self._status, headers=self._headers)

    def __repr__(self):
        return """{class_name}()""".format(class_name=self.__class__.__name__)


def create_response_factory():
    """Create and prepare response factory.

    :returns: instance of :class:`ResponseFactory <looseserver.common.response.ResponseFactory>`.
    """
    response_factory = ResponseFactory()

    server_factory_preparator = ResponseFactoryPreparator(response_factory=response_factory)
    server_factory_preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

    return response_factory
