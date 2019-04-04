"""Module with client to configure server via HTTP protocol."""

import requests

from looseserver.common.api import APIError
from looseserver.client.abstract import AbstractClient


class HTTPClient(AbstractClient):
    """Class to configure a server via HTTP protocol."""

    def _send_request(self, url, method="GET", json=None):
        """Make a request.

        :param url: url to make a request.
        :param method: request method.
        :param json: json payload for the request.
        :returns: parsed json response.
        :raises: :class:`APIError <looseserver.common.api.APIError>` if response
            contains error from API.
            :class:`HTTPError` is the cause of the error is not API.
        """
        absolute_url = self._build_url(relative_url=url)
        response = requests.request(url=absolute_url, method=method, json=json)
        try:
            response.raise_for_status()
        except requests.HTTPError as http_error:
            try:
                description = response.json()["error"]["description"]
            except Exception:   # pylint: disable=broad-except
                raise http_error
            else:
                raise APIError(description=description) from http_error

        return response.json().get("data")
