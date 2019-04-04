"""Module with client to configure server as a flask application."""

from looseserver.common.api import APIError
from looseserver.client.abstract import AbstractClient


class FlaskClient(AbstractClient):
    """Class to configure a server as a flask application."""

    def __init__(self, base_url, application_client, rule_factory=None, response_factory=None):
        super(FlaskClient, self).__init__(
            base_url=base_url,
            rule_factory=rule_factory,
            response_factory=response_factory,
            )

        self._application_client = application_client

    def _send_request(self, url, method="GET", json=None):
        """Make a request.

        :param url: url to make a request.
        :param method: request method.
        :param json: json payload for the request.
        :returns: parsed json response.
        :raises: :class:`APIError <looseserver.common.api.APIError>` if response
            contains error from API.
        """
        absolute_url = self._build_url(relative_url=url)
        response = self._application_client.open(absolute_url, method=method, json=json)

        if response.status_code >= 400:
            description = response.json["error"]["description"]
            raise APIError(description)

        return response.json.get("data")
