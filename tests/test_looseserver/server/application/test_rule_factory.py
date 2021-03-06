"""Test cases for rule factory."""

import string
import random
from urllib.parse import urljoin

from looseserver.common.rule import RuleFactory
from looseserver.server.application import configure_application, DEFAULT_CONFIGURATION_ENDPOINT


def test_rule_factory(server_response_factory, server_rule_prototype):
    """Check that custom rule factory is used when specified.

    1. Create rule factory.
    2. Register a new rule type.
    3. Configure application with the created rule factory.
    4. Make a POST-request to create a method rule for PUT requests.
    5. Check that response is successful and contains rule ID.
    """
    rule_factory = RuleFactory()
    application = configure_application(
        rule_factory=rule_factory,
        response_factory=server_response_factory,
        )

    rule_type = "".join(random.choice(string.ascii_uppercase) for _ in range(10))
    rule = server_rule_prototype.create_new(rule_type=rule_type)

    rule_factory.register_rule(
        rule_type=rule_type,
        parser=lambda *args, **kwargs: rule,
        serializer=lambda *args, **kwargs: {},
        )
    serialized_rule = rule_factory.serialize_rule(rule=rule)

    http_response = application.test_client().post(
        urljoin(DEFAULT_CONFIGURATION_ENDPOINT, "rules"),
        json=serialized_rule,
        )
    assert http_response.status_code == 200, "Can't create a rule"
    assert http_response.json["data"]["rule_id"] is not None, "Response does not contain rule ID"
