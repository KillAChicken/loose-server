"""Configuration of pytest."""

from urllib.parse import urljoin

import flask
import pytest


# pylint: disable=redefined-outer-name
@pytest.fixture
def managed_application(base_endpoint, core_manager):
    """Application with configured core manager."""
    application = flask.Flask("TestApplication")

    application.add_url_rule(
        rule=base_endpoint,
        endpoint="base",
        view_func=core_manager.view,
        methods=["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"],
        )

    application.add_url_rule(
        rule=urljoin(base_endpoint, "<path:path>"),
        endpoint="routes",
        view_func=core_manager.view,
        methods=["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"],
        )
    return application


@pytest.fixture
def http_client(managed_application):
    """Client for the managed application."""
    return managed_application.test_client()
# pylint: enable=redefined-outer-name
