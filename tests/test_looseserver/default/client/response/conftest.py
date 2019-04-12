"""Configuration of pytest."""

import pytest

from looseserver.client.flask import FlaskClient
from looseserver.default.client.rule import MethodRule


@pytest.fixture
def existing_get_rule(configuration_endpoint, default_factories_application):
    """Rule that matches every GET-request."""
    client = FlaskClient(
        base_url=configuration_endpoint,
        application_client=default_factories_application.test_client(),
        )
    return client.create_rule(rule=MethodRule(method="GET"))
