"""Test cases for flask clients."""

import pytest

from looseserver.common.api import APIError
from looseserver.default.common.constants import RuleType
from looseserver.default.server.rule import create_rule_factory, MethodRule as ServerMethodRule
from looseserver.server.application import configure_application
from looseserver.client.rule import ClientRule
from looseserver.client.flask import FlaskClient


def test_successful_request(rule_factory):
    """Check that flask client can send a request and handle successful response.

    1. Create a rule factory with method rule for the client.
    2. Configure application with default rule factory.
    3. Create a rule with the client.
    4. Check the rule.
    """
    base_endpoint = "/base/"
    configuration_endpoint = "/config/"
    server_rule_factory = create_rule_factory(base_url=base_endpoint)

    application = configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        rule_factory=server_rule_factory,
        )

    rule_type = RuleType.METHOD.name

    serialized_server_rule = server_rule_factory.serialize_rule(
        rule=ServerMethodRule(rule_type=rule_type, method="GET"),
        )

    rule_factory.register_rule(
        rule_type=rule_type,
        parser=lambda *args, **kwargs: ClientRule(rule_type=rule_type),
        serializer=lambda *args, **kwargs: serialized_server_rule["parameters"],
        )

    client = FlaskClient(
        base_url=configuration_endpoint,
        rule_factory=rule_factory,
        application_client=application.test_client(),
        )

    created_rule = client.create_rule(rule=ClientRule(rule_type=rule_type))
    assert created_rule.rule_id is not None, "Rule ID has not been set"


def test_failed_request():
    """Check that flask client can handle failed response.

    1. Configure application.
    2. Try to get a non-existing rule with the client.
    3. Check that APIError is raised.
    """
    configuration_endpoint = "/config/"
    application = configure_application(configuration_endpoint=configuration_endpoint)

    client = FlaskClient(
        base_url=configuration_endpoint,
        application_client=application.test_client(),
        )

    with pytest.raises(APIError) as exception_info:
        client.get_rule(rule_id="FakeID")

    assert exception_info.value.description == "Failed to find rule with ID 'FakeID'", (
        "Wrong APIError is raised"
        )
