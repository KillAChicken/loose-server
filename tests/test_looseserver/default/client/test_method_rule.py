"""Test cases for MethodRule."""

from looseserver.default.common.constants import RuleType
from looseserver.default.common.configuration import RuleFactoryPreparator
from looseserver.default.client.rule import MethodRule
from looseserver.server.application import configure_application
from looseserver.client.flask import FlaskClient


def test_default_rule_type():
    """Check the default rule type of the method rule.

    1. Create a method rule without specifying its type.
    2. Check the rule type.
    """
    rule = MethodRule(method="GET")
    assert rule.rule_type == RuleType.METHOD.name, "Wrong rule type"


def test_rule_representation():
    """Check the representation of the method rule.

    1. Create a method rule.
    2. Check result of the repr function.
    """
    rule = MethodRule(method="POST")
    assert repr(rule) == "MethodRule(method='POST')", "Wrong representation"


def test_creation(configuration_endpoint, rule_factory):
    """Check that MethodRule can be created.

    1. Configure application with default rule factory.
    2. Prepare method rule in the rule factory of the flask client.
    3. Create a method rule with the client.
    4. Check the created rule.
    """
    application = configure_application(configuration_endpoint=configuration_endpoint)

    preparator = RuleFactoryPreparator(rule_factory)
    preparator.prepare_method_rule(method_rule_class=MethodRule)

    client = FlaskClient(
        base_url=configuration_endpoint,
        rule_factory=rule_factory,
        application_client=application.test_client(),
        )

    rule_spec = MethodRule(method="PUT")
    rule = client.create_rule(rule=rule_spec)

    assert rule.rule_id is not None, "Rule was not created"
    assert rule.method == rule_spec.method, "Wrong method"
