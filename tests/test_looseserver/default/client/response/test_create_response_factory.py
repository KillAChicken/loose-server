"""Test cases for creation of the default response factory."""

from looseserver.default.client.rule import create_rule_factory, MethodRule
from looseserver.default.client.response import create_response_factory, FixedResponse
from looseserver.client.flask import FlaskClient


def test_create_response_factory(
        base_endpoint,
        configuration_endpoint,
        default_factories_application,
    ):
    """Check that default responses are registered in the default response factory.

    1. Configure application with default factories.
    2. Create default response factory for client.
    3. Create a method rule with the client.
    4. Set a fixed response with the client.
    4. Check that response is successful.
    """
    application_client = default_factories_application.test_client()

    client = FlaskClient(
        configuration_url=configuration_endpoint,
        rule_factory=create_rule_factory(base_url=base_endpoint),
        response_factory=create_response_factory(),
        application_client=application_client,
        )

    rule = client.create_rule(rule=MethodRule(method="GET"))

    fixed_response = FixedResponse(status=200)
    client.set_response(rule_id=rule.rule_id, response=fixed_response)

    assert application_client.get(base_endpoint).status_code == fixed_response.status, (
        "Response was not set"
        )
