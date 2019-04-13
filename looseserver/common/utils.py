"""Module with common helper functions."""

import urllib.parse as urlparse


def ensure_endpoint(endpoint):
    """Ensure that endpoint starts and ends with slashes.

    :param endpoint: string endpoint.
    :returns: the same string starting and ending with slashes.
    """
    ensured_endpoint = urlparse.urljoin("/", endpoint)
    if not ensured_endpoint.endswith("/"):
        ensured_endpoint += "/"
    return ensured_endpoint
