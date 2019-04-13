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


def test_response_factory(
        server_rule_factory,
        registered_match_all_rule,
        server_response_prototype,
    ):
    """Check that custom response factory is used when specified.

    1. Create a response factory.
    2. Register a new response type.
    3. Configure application with the created response factory.
    4. Create a univeral rule to match every request.
    5. Make a POST-request to set a response for the rule.
    6. Check that response is successful.
    7. Make a request to the base url.
    8. Check the response.
    """
    response_factory = ResponseFactory()

    application = configure_application(
        rule_factory=server_rule_factory,
        response_factory=response_factory,
        )
    client = application.test_client()

    serialized_rule = server_rule_factory.serialize_rule(registered_match_all_rule)
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
