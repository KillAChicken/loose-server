"""Module with base client for server configuration."""

import urllib.parse as urlparse

from looseserver.default.client.rule import create_rule_factory
from looseserver.default.client.response import create_response_factory


class AbstractClient:
    """Abstract class to manage configuration."""

    def __init__(self, base_url, rule_factory=None, response_factory=None):
        self._base_url = base_url

        if rule_factory is None:
            rule_factory = create_rule_factory(base_url=base_url)
        self._rule_factory = rule_factory

        if response_factory is None:
            response_factory = create_response_factory()
        self._response_factory = response_factory

    def _build_url(self, relative_url):
        """Buile absolute url.

        :param relative_url: relative path of the endpoint.
        :returns: absolute url.
        """
        return urlparse.urljoin(self._base_url, relative_url)

    def _send_request(self, url, method="GET", json=None):
        """Make a request.

        :param url: url to make a request.
        :param method: request method.
        :param json: json payload for the request.
        :returns: parsed json response.
        :raises: :class:`APIError <looseserver.common.api.APIError>` if response
            contains error from API.
        """
        raise NotImplementedError("Method to send request has not been implemeneted")

    def create_rule(self, rule):
        """Create a rule.

        :param rule: instance of :class:`ClientRule <looseserver.client.rule.ClientRule>`.
        :returns: rule created by rule factory.
        """
        rule_data = self._rule_factory.serialize_rule(rule)
        created_rule_data = self._send_request(url="rules", method="POST", json=rule_data)
        rule = self._rule_factory.parse_rule(created_rule_data)
        rule.rule_id = created_rule_data["rule_id"]
        return rule

    def get_rule(self, rule_id):
        """Get rule by its ID.

        :param rule_id: string with rule ID.
        :returns: rule created by rule factory.
        """
        rule_url = "rule/{0}".format(rule_id)
        rule_data = self._send_request(url=rule_url)
        rule = self._rule_factory.parse_rule(rule_data)
        rule.rule_id = rule_id
        return rule

    def set_response(self, rule_id, response):
        """Set response for the rule.

        :param rule_id: string with rule ID.
        :param rule: instance of
            :class:`ClientResponse <looseserver.client.response.ClientResponse>`.
        :returns: response created by response factory.
        """
        response_url = "response/{0}".format(rule_id)
        response_parameters = self._response_factory.serialize_response(response)
        response_data = self._send_request(
            url=response_url,
            method="POST",
            json=response_parameters,
            )
        response = self._response_factory.parse_response(response_data)
        return response
