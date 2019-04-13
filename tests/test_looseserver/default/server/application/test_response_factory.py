"""Test cases for response factory."""

import string
import random
from urllib.parse import urljoin

from looseserver.common.response import ResponseFactory
from looseserver.server.application import DEFAULT_BASE_ENDPOINT, DEFAULT_CONFIGURATION_ENDPOINT
from looseserver.client.flask import FlaskClient
from looseserver.default.server.application import configure_application


def test_default_response_factory(
        client_rule_factory,
        client_response_factory,
        client_method_rule_class,
        client_fixed_response_class,
    ):
    """Check that default response factory is used if custom one is not specified.

    1. Configure application without specifying response factory.
    2. Create a flask client.
    3. Create a GET-rule and set a response for it.
    4. Make a request to the base url.
    5. Check the response.
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


def test_response_factory(
        client_rule_factory,
        client_response_factory,
        client_method_rule_class,
        server_response_prototype,
    ):
    """Check that custom response factory is used when specified.

    1. Create a response factory.
    2. Register a new response type.
    3. Configure application with the created response factory.
    4. Create a flask client.
    5. Create a PUT-rule with the client.
    6. Make a POST-request to set a response for the rule.
    7. Check that response is successful.
    8. Make a request to the base url.
    9. Check the response.
    """
    response_factory = ResponseFactory()

    application = configure_application(response_factory=response_factory)

    application_client = application.test_client()

    client = FlaskClient(
        rule_factory=client_rule_factory,
        response_factory=client_response_factory,
        configuration_url=DEFAULT_CONFIGURATION_ENDPOINT,
        application_client=application_client,
        )

    rule_id = client.create_rule(client_method_rule_class(method="PUT")).rule_id

    response_type = "".join(random.choice(string.ascii_uppercase) for _ in range(10))
    response = server_response_prototype.create_new(
        response_type=response_type,
        builder_implementation=lambda *args, **kwargs: b"body",
        )

    response_factory.register_response(
        response_type=response_type,
        parser=lambda *args, **kwargs: response,
        serializer=lambda *args, **kwargs: {},
        )

    serialized_response = response_factory.serialize_response(response=response)

    http_response = application_client.post(
        urljoin(DEFAULT_CONFIGURATION_ENDPOINT, "response/{0}".format(rule_id)),
        json=serialized_response,
        )
    assert http_response.status_code == 200, "Can't set a response"

    assert application_client.put(DEFAULT_BASE_ENDPOINT).data == b"body"
