"""Test cases for creation of the default rule factory."""

from looseserver.default.client.rule import create_rule_factory, PathRule, MethodRule, CompositeRule
from looseserver.client.flask import FlaskClient


def test_create_rule_factory(base_endpoint, configuration_endpoint, default_factories_application):
    """Check that default rules are registered in the default rule factory.

    1. Configure application with default rule factory.
    2. Create default rule factory for client.
    3. Create a path, method and composite rules with the client.
    4. Check that responses are successful.
    """
    rule_factory = create_rule_factory(base_url=base_endpoint)

    client = FlaskClient(
        base_url=configuration_endpoint,
        rule_factory=rule_factory,
        application_client=default_factories_application.test_client(),
        )

    path_rule_spec = PathRule(path="path")
    path_rule = client.create_rule(rule=path_rule_spec)
    assert path_rule.rule_id is not None, "Rule was not created"

    method_rule_spec = MethodRule(method="DELETE")
    method_rule = client.create_rule(rule=method_rule_spec)
    assert method_rule.rule_id is not None, "Rule was not created"

    composite_rule_spec = CompositeRule(children=[path_rule_spec, method_rule_spec])
    composite_rule = client.create_rule(rule=composite_rule_spec)
    assert composite_rule.rule_id is not None, "Rule was not created"
