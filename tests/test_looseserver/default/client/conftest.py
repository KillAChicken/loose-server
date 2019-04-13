"""Configuration of pytest."""

import pytest

from looseserver.default.server.application import configure_application
from looseserver.client.flask import FlaskClient


# pylint: disable=redefined-outer-name
@pytest.fixture
def default_factories_application(base_endpoint, configuration_endpoint):
    """Configured application with default factories."""
    return configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        )


@pytest.fixture
def configured_flask_client(
        configuration_endpoint,
        client_rule_factory,
        client_response_factory,
        default_factories_application,
    ):
    """Configured flask client for the application with default factories."""
    return FlaskClient(
        configuration_url=configuration_endpoint,
        rule_factory=client_rule_factory,
        response_factory=client_response_factory,
        application_client=default_factories_application.test_client(),
        )
# pylint: enable=redefined-outer-name
