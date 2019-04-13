"""Module with base client for server configuration."""

from abc import ABC, abstractmethod

import urllib.parse as urlparse


class AbstractClient(ABC):
    """Abstract class to manage configuration."""

    def __init__(self, configuration_url, rule_factory, response_factory):
        self._configuration_url = configuration_url
        self._rule_factory = rule_factory
        self._response_factory = response_factory

    def _build_url(self, relative_url):
        """Buile absolute url.

        :param relative_url: relative path of the endpoint.
        :returns: absolute url.
        """
        return urlparse.urljoin(self._configuration_url, relative_url)

    @abstractmethod
    def _send_request(self, url, method="GET", json=None):
        """Make a request.

        :param url: url to make a request.
        :param method: request method.
        :param json: json payload for the request.
        :returns: parsed json response.
        :raises: :class:`APIError <looseserver.common.api.APIError>` if response
            contains error from API.
        """

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

    def remove_rule(self, rule_id):
        """Remove rule by its ID.

        :param rule_id: string with rule ID.
        """
        rule_url = "rule/{0}".format(rule_id)
        self._send_request(url=rule_url, method="DELETE")

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
