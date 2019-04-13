"""Test cases for configuration endpoint."""

import pytest

from looseserver.server.application import DEFAULT_BASE_ENDPOINT, DEFAULT_CONFIGURATION_ENDPOINT
from looseserver.client.flask import FlaskClient
from looseserver.default.server.application import configure_application


def test_default_configuration_endpoint(
        client_rule_factory,
        client_response_factory,
        client_method_rule_class,
        client_fixed_response_class,
    ):
    """Test the default configuration endpoint of the application.

    1. Configure application without specifying configuration endpoint.
    2. Create a flask client with default configuration endpoint.
    3. Create a rule with the client (RulesManager resource).
    4. Get the rule with the client (Rule resource).
    5. Set a response for the rule with the client (Response resource).
    6. Make a request to trigger the configured rule and response.
    7. Check the response.
    """
    application = configure_application()
    client = FlaskClient(
        rule_factory=client_rule_factory,
        response_factory=client_response_factory,
        configuration_url=DEFAULT_CONFIGURATION_ENDPOINT,
        application_client=application.test_client(),
        )

    rule_id = client.create_rule(client_method_rule_class(method="GET")).rule_id
    client.set_response(rule_id=rule_id, response=client_fixed_response_class(status=200))

    assert application.test_client().get(DEFAULT_BASE_ENDPOINT).status_code == 200, "Wrong status"


@pytest.mark.parametrize(
    argnames="specified_endpoint,expected_endpoint",
    argvalues=[
        ("/config/", "/config/"),
        ("config/", "/config/"),
        ("/config", "/config/"),
        ],
    ids=[
        "Both slashes",
        "Missing slash at the beginning",
        "Missing slash at the end",
        ],
    )
def test_configuration_endpoint(
        client_rule_factory,
        client_response_factory,
        client_method_rule_class,
        client_fixed_response_class,
        specified_endpoint,
        expected_endpoint,
    ):
    # pylint: disable=too-many-arguments
    """Test that specified configuration endpoint is used.

    1. Configure application with specifying configuration endpoint.
    2. Create a flask client with expected configuration endpoint.
    3. Create a rule with the client (RulesManager resource).
    4. Get the rule with the client (Rule resource).
    5. Set a response for the rule with the client (Response resource).
    6. Make a request to trigger the configured rule and response.
    7. Check the response.
    """
    application = configure_application(configuration_endpoint=specified_endpoint)

    client = FlaskClient(
        rule_factory=client_rule_factory,
        response_factory=client_response_factory,
        configuration_url=expected_endpoint,
        application_client=application.test_client(),
        )

    rule_id = client.create_rule(client_method_rule_class(method="GET")).rule_id
    client.set_response(rule_id=rule_id, response=client_fixed_response_class(status=200))

    assert application.test_client().get(DEFAULT_BASE_ENDPOINT).status_code == 200, "Wrong status"
