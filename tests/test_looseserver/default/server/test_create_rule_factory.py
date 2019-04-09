"""Test cases for creation of the default rule factory."""

from urllib.parse import urljoin

from looseserver.server.application import configure_application
from looseserver.default.common.constants import RuleType
from looseserver.default.server.rule import create_rule_factory, PathRule, MethodRule, CompositeRule


def test_create_rule_factory():
    """Check that default rules are registered in the default rule factory.

    1. Create default rule factory.
    2. Configure application with the rule factory.
    3. Make a 3 POST-request to create a path, method and composite rules.
    4. Check that responses are successful.
    """
    base_endpoint = "/base/"
    configuration_endpoint = "/config/"
    rule_factory = create_rule_factory(base_url=base_endpoint)

    application = configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        rule_factory=rule_factory,
        )

    client = application.test_client()
    new_rule_endpoint = urljoin(configuration_endpoint, "rules")

    path_rule = PathRule(rule_type=RuleType.PATH.name, path="path")
    serialized_path_rule = rule_factory.serialize_rule(rule=path_rule)

    path_rule_response = client.post(new_rule_endpoint, json=serialized_path_rule)
    assert path_rule_response.status_code == 200, "Can't create a rule"
    assert path_rule_response.json["data"]["rule_id"] is not None, "No rule ID in the response"

    method_rule = MethodRule(rule_type=RuleType.METHOD.name, method="DELETE")
    serialized_method_rule = rule_factory.serialize_rule(rule=method_rule)

    method_rule_response = client.post(new_rule_endpoint, json=serialized_method_rule)
    assert method_rule_response.status_code == 200, "Can't create a rule"
    assert method_rule_response.json["data"]["rule_id"] is not None, "No rule ID in the response"

    composite_rule = CompositeRule(
        rule_type=RuleType.COMPOSITE.name,
        children=[path_rule, method_rule],
        )
    serialized_composite_rule = rule_factory.serialize_rule(rule=composite_rule)

    composite_rule_response = client.post(new_rule_endpoint, json=serialized_composite_rule)
    assert composite_rule_response.status_code == 200, "Can't create a rule"
    assert composite_rule_response.json["data"]["rule_id"] is not None, "No rule ID in the response"
