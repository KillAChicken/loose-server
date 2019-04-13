"""Module with client to configure server via HTTP protocol."""

from looseserver.client.http import HTTPClient as BaseHTTPClient
from looseserver.default.client.rule import create_rule_factory
from looseserver.default.client.response import create_response_factory


class HTTPClient(BaseHTTPClient):
    """Class to configure a server via HTTP protocol."""

    def __init__(self, configuration_url, rule_factory=None, response_factory=None):
        if rule_factory is None:
            rule_factory = create_rule_factory()

        if response_factory is None:
            response_factory = create_response_factory()

        super(HTTPClient, self).__init__(
            configuration_url=configuration_url,
            rule_factory=rule_factory,
            response_factory=response_factory,
            )
