"""Configuration of pytest."""

import pytest

from looseserver.client.flask import FlaskClient
from looseserver.default.client.rule import create_rule_factory, MethodRule


@pytest.fixture
def existing_get_rule(
        base_endpoint,
        configuration_endpoint,
        default_factories_application,
        client_response_factory,
    ):
    """Rule that matches every GET-request."""
    client = FlaskClient(
        configuration_url=configuration_endpoint,
        rule_factory=create_rule_factory(base_url=base_endpoint),
        response_factory=client_response_factory,
        application_client=default_factories_application.test_client(),
        )
    return client.create_rule(rule=MethodRule(method="GET"))
