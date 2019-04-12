"""Configuration of pytest."""

from urllib.parse import urljoin

import flask
import pytest


@pytest.fixture
def managed_application_client(base_endpoint, core_manager):
    """Test client of the configured flask application."""
    application = flask.Flask("TestApplication")

    methods = ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]

    application.add_url_rule(
        rule=base_endpoint,
        endpoint="base",
        view_func=core_manager.view,
        methods=methods,
        )

    application.add_url_rule(
        rule=urljoin(base_endpoint, "<path:path>"),
        endpoint="routes",
        view_func=core_manager.view,
        methods=methods,
        )
    return application.test_client()
