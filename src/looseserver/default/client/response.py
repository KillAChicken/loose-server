"""Default client responses."""

from copy import copy

from looseserver.client.response import ClientResponse
from looseserver.common.response import ResponseFactory
from looseserver.default.common.constants import ResponseType
from looseserver.default.common.configuration import ResponseFactoryPreparator


class FixedResponse(ClientResponse):
    """Response that does not depend on request or rule."""

    def __init__(self, body="", status=200, headers=(), response_type=ResponseType.FIXED.name):
        super(FixedResponse, self).__init__(response_type)
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

    def __repr__(self):
        return "{class_name}()".format(class_name=self.__class__.__name__)


def create_response_factory():
    """Create and prepare response factory.

    :returns: instance of :class:`ResponseFactory <looseserver.common.response.ResponseFactory>`.
    """
    response_factory = ResponseFactory()

    client_factory_preparator = ResponseFactoryPreparator(response_factory=response_factory)
    client_factory_preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

    return response_factory
