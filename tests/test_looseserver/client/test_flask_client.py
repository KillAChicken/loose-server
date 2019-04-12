"""Test cases for flask clients."""

import pytest

from looseserver.common.api import APIError
from looseserver.client.flask import FlaskClient


def test_successful_request(
        configuration_endpoint,
        application_factory,
        client_rule_factory,
        registered_rule,
    ):
    """Check that flask client can send a request and handle successful response.

    1. Create a rule with the client.
    2. Check the rule.
    """
    application = application_factory()

    client = FlaskClient(
        base_url=configuration_endpoint,
        rule_factory=client_rule_factory,
        application_client=application.test_client(),
        )

    created_rule = client.create_rule(rule=registered_rule)
    assert created_rule.rule_id is not None, "Rule ID has not been set"


def test_failed_request(configuration_endpoint, application_factory):
    """Check that flask client can handle failed response.

    1. Try to get a non-existing rule with the client.
    2. Check that APIError is raised.
    """
    application = application_factory()

    client = FlaskClient(
        base_url=configuration_endpoint,
        application_client=application.test_client(),
        )

    with pytest.raises(APIError) as exception_info:
        client.get_rule(rule_id="FakeID")

    assert exception_info.value.description == "Failed to find rule with ID 'FakeID'", (
        "Wrong APIError is raised"
        )
