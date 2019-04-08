"""Test cases for response factory."""

import string
import random
from urllib.parse import urljoin

from looseserver.common.response import ResponseFactory
from looseserver.server.application import (
    configure_application,
    DEFAULT_BASE_ENDPOINT,
    DEFAULT_CONFIGURATION_ENDPOINT,
    )
from looseserver.default.common.constants import RuleType, ResponseType
from looseserver.default.server.rule import create_rule_factory, MethodRule
from looseserver.default.server.response import create_response_factory, FixedResponse


def test_default_response_factory():
    """Check that default response factory is used if custom one is not specified.

    1. Configure application without specifying response factory.
    2. Create a method rule for PUT-requests.
    3. Make a POST-request to set a fixed response for the rule.
    4. Check that response is successful.
    5. Make a PUT-request to the base url.
    6. Check the response.
    """
    rule_factory = create_rule_factory(base_url=DEFAULT_BASE_ENDPOINT)
    application = configure_application(rule_factory=rule_factory)

    rule = MethodRule(rule_type=RuleType.METHOD.name, method="PUT")
    serialized_rule = rule_factory.serialize_rule(rule=rule)

    client = application.test_client()

    http_response = client.post(
        urljoin(DEFAULT_CONFIGURATION_ENDPOINT, "rules"),
        json=serialized_rule,
        )
    rule_id = http_response.json["data"]["rule_id"]

    default_response_factory = create_response_factory()

    response = FixedResponse(response_type=ResponseType.FIXED.name, body="body")
    serialized_response = default_response_factory.serialize_response(response=response)

    http_response = client.post(
        urljoin(DEFAULT_CONFIGURATION_ENDPOINT, "response/{0}".format(rule_id)),
        json=serialized_response,
        )

    assert http_response.status_code == 200, "Can't set a response"
    assert client.put(DEFAULT_BASE_ENDPOINT).data == b"body"


def test_response_factory(server_response_prototype):
    """Check that custom response factory is used when specified.

    1. Create a response factory.
    2. Register a new response type.
    3. Configure application with the created response factory.
    4. Create a method rule for PUT-requests.
    5. Make a POST-request to set a response for the rule.
    6. Check that response is successful.
    7. Make a PUT-request to the base url.
    8. Check the response.
    """
    rule_factory = create_rule_factory(base_url=DEFAULT_BASE_ENDPOINT)
    response_factory = ResponseFactory()

    application = configure_application(
        rule_factory=rule_factory,
        response_factory=response_factory,
        )

    rule = MethodRule(rule_type=RuleType.METHOD.name, method="PUT")
    serialized_rule = rule_factory.serialize_rule(rule=rule)

    client = application.test_client()

    http_response = client.post(
        urljoin(DEFAULT_CONFIGURATION_ENDPOINT, "rules"),
        json=serialized_rule,
        )
    rule_id = http_response.json["data"]["rule_id"]

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

    http_response = client.post(
        urljoin(DEFAULT_CONFIGURATION_ENDPOINT, "response/{0}".format(rule_id)),
        json=serialized_response,
        )

    assert http_response.status_code == 200, "Can't set a response"
    assert client.put(DEFAULT_BASE_ENDPOINT).data == b"body"
