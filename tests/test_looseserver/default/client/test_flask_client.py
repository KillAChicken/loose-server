"""Test cases for flask clients."""

import string
import random

from looseserver.server.application import DEFAULT_BASE_ENDPOINT, DEFAULT_CONFIGURATION_ENDPOINT
from looseserver.client.rule import ClientRule
from looseserver.client.response import ClientResponse
from looseserver.default.server.application import configure_application
from looseserver.default.client.rule import MethodRule
from looseserver.default.client.response import FixedResponse
from looseserver.default.client.flask import FlaskClient


def test_default_factories():
    """Check that default factories are used if None was specified.

    1. Create default application.
    2. Create a flask client without specifying rule factory.
    3. Create a method rule with the client.
    4. Set a fixed response with the client.
    5. Check the response.
    """
    application = configure_application()
    application_client = application.test_client()

    client = FlaskClient(
        configuration_url=DEFAULT_CONFIGURATION_ENDPOINT,
        application_client=application.test_client(),
        )

    rule = client.create_rule(rule=MethodRule(method="GET"))
    assert rule.rule_id is not None, "Rule was not created"

    client.set_response(rule_id=rule.rule_id, response=FixedResponse(status=200))

    assert application_client.get(DEFAULT_BASE_ENDPOINT).status_code == 200, "Wrong status"


def test_custom_factories(
        server_rule_factory,
        server_response_factory,
        client_rule_factory,
        client_response_factory,
        server_rule_prototype,
        server_response_prototype,
    ):
    # pylint: disable=too-many-arguments
    """Check that custom factories are used if specified.

    1. Register new rule in the server and client factories.
    2. Register new response in the server and client factories.
    3. Create an application with server factories.
    4. Create a flask client with server factories.
    5. Create a rule with the client.
    6. Set a response with the client.
    7. Check the response.
    """
    serializer = lambda *args, **kwargs: None

    rule_type = "".join(random.choice(string.ascii_uppercase) for _ in range(5))

    server_rule = server_rule_prototype.create_new(rule_type=rule_type, match_implementation=True)
    server_rule_factory.register_rule(
        rule_type=rule_type,
        parser=lambda *args, **kwargs: server_rule,
        serializer=serializer,
        )

    client_rule_factory.register_rule(
        rule_type=rule_type,
        parser=lambda *args, **kwargs: ClientRule(rule_type=rule_type),
        serializer=serializer,
        )

    response_type = "".join(random.choice(string.ascii_uppercase) for _ in range(5))

    server_response = server_response_prototype.create_new(
        response_type=response_type,
        builder_implementation="",
        )

    server_response_factory.register_response(
        response_type=response_type,
        parser=lambda *args, **kwargs: server_response,
        serializer=serializer,
        )

    client_response_factory.register_response(
        response_type=response_type,
        parser=lambda *args, **kwargs: ClientResponse(response_type=response_type),
        serializer=serializer,
        )

    application = configure_application(
        rule_factory=server_rule_factory,
        response_factory=server_response_factory,
        )

    application_client = application.test_client()

    client = FlaskClient(
        configuration_url=DEFAULT_CONFIGURATION_ENDPOINT,
        application_client=application.test_client(),
        rule_factory=client_rule_factory,
        response_factory=client_response_factory,
        )

    rule = client.create_rule(rule=ClientRule(rule_type=rule_type))
    assert rule.rule_id is not None, "Rule was not created"

    client.set_response(rule_id=rule.rule_id, response=ClientResponse(response_type=response_type))

    assert application_client.get(DEFAULT_BASE_ENDPOINT).status_code == 200, "Wrong status"
