"""Test cases for CompositeRule."""

from urllib.parse import urljoin

from looseserver.server.application import configure_application
from looseserver.default.common.constants import RuleType
from looseserver.default.common.configuration import RuleFactoryPreparator
from looseserver.default.server.rule import PathRule, MethodRule, CompositeRule


def test_rule_representation():
    """Check the representation of the composite rule.

    1. Create a composite rule with 2 children.
    2. Check result of the repr function.
    """
    path_rule = PathRule(rule_type=RuleType.PATH.name, path="")
    method_rule = MethodRule(rule_type=RuleType.METHOD.name, method="GET")

    children = [path_rule, method_rule]
    composite_rule = CompositeRule(rule_type=RuleType.COMPOSITE.name, children=children)

    assert repr(composite_rule) == "CompositeRule(children={0})".format(tuple(children)), (
        "Wrong representation"
        )


def test_composite_rule_match_found(rule_factory, response_factory, response_200):
    """Check that CompositeRule is triggered when all child rules are triggered.

    1. Prepare path, method and composite rules in the rule factory.
    2. Configure application with the rule factory.
    3. Make a POST-request to create a composite rule with 2 children: path and method rules.
    4. Set a response for the rule.
    5. Make a request of the specified type to the specified path.
    6. Check that the rule finds a match.
    """
    base_endpoint = "/base/"
    configuration_endpoint = "/config/"

    preparator = RuleFactoryPreparator(rule_factory)
    preparator.prepare_path_rule(path_rule_class=PathRule, base_url=base_endpoint)
    preparator.prepare_method_rule(method_rule_class=MethodRule)
    preparator.prepare_composite_rule(composite_rule_class=CompositeRule)

    application = configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        rule_factory=rule_factory,
        response_factory=response_factory,
        )

    path = "test"
    method = "POST"

    composite_rule = CompositeRule(
        rule_type=RuleType.COMPOSITE.name,
        children=[
            PathRule(rule_type=RuleType.PATH.name, path=path),
            MethodRule(rule_type=RuleType.METHOD.name, method=method),
            ],
        )

    serialized_rule = rule_factory.serialize_rule(rule=composite_rule)

    client = application.test_client()

    http_response = client.post(urljoin(configuration_endpoint, "rules"), json=serialized_rule)

    assert http_response.status_code == 200, "Can't create a rule"

    rule_id = http_response.json["data"]["rule_id"]

    serialized_response = response_factory.serialize_response(response=response_200)

    http_response = client.post(
        urljoin(configuration_endpoint, "response/{0}".format(rule_id)),
        json=serialized_response,
        )
    assert http_response.status_code == 200, "Can't set a response"

    assert client.open(urljoin(base_endpoint, path), method=method).status_code == 200, (
        "Wrong status code"
        )


def test_composite_rule_no_match(rule_factory, response_factory, response_200):
    """Check that CompositeRule is not triggered if any of the child rules is not triggered.

    1. Prepare method and composite rules in the rule factory.
    2. Configure application with the rule factory.
    3. Make a POST-request to create a composite rule with 2 method rules for different methods.
    4. Set a response for the rule.
    5. Make 2 requests of the specified types to the base endpoint.
    6. Check that the rule does not find a match.
    """
    base_endpoint = "/base/"
    configuration_endpoint = "/config/"

    preparator = RuleFactoryPreparator(rule_factory)
    preparator.prepare_method_rule(method_rule_class=MethodRule)
    preparator.prepare_composite_rule(composite_rule_class=CompositeRule)

    application = configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        rule_factory=rule_factory,
        response_factory=response_factory,
        )

    first_rule = MethodRule(rule_type=RuleType.METHOD.name, method="GET")
    second_rule = MethodRule(rule_type=RuleType.METHOD.name, method="POST")

    composite_rule = CompositeRule(
        rule_type=RuleType.COMPOSITE.name,
        children=[first_rule, second_rule],
        )

    serialized_rule = rule_factory.serialize_rule(rule=composite_rule)

    client = application.test_client()

    http_response = client.post(urljoin(configuration_endpoint, "rules"), json=serialized_rule)

    assert http_response.status_code == 200, "Can't create a rule"

    rule_id = http_response.json["data"]["rule_id"]

    serialized_response = response_factory.serialize_response(response=response_200)

    http_response = client.post(
        urljoin(configuration_endpoint, "response/{0}".format(rule_id)),
        json=serialized_response,
        )
    assert http_response.status_code == 200, "Can't set a response"

    assert client.get(base_endpoint).status_code == 404, "Wrong status code"
    assert client.post(base_endpoint).status_code == 404, "Wrong status code"


def test_no_children(rule_factory, response_factory, response_200):
    """Check that composite rule is not triggered without children.

    1. Prepare composite rule in the rule factory.
    2. Configure application with the rule factory.
    3. Make a POST-request to create a composite rule without children.
    4. Set a response for the rule.
    5. Make a request to the base endpoint.
    6. Check that the rule does not find a match.
    """
    base_endpoint = "/base/"
    configuration_endpoint = "/config/"

    preparator = RuleFactoryPreparator(rule_factory)
    preparator.prepare_composite_rule(composite_rule_class=CompositeRule)

    application = configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        rule_factory=rule_factory,
        response_factory=response_factory,
        )

    composite_rule = CompositeRule(rule_type=RuleType.COMPOSITE.name, children=())
    serialized_rule = rule_factory.serialize_rule(rule=composite_rule)

    client = application.test_client()

    http_response = client.post(urljoin(configuration_endpoint, "rules"), json=serialized_rule)

    assert http_response.status_code == 200, "Can't create a rule"

    rule_id = http_response.json["data"]["rule_id"]

    serialized_response = response_factory.serialize_response(response=response_200)

    http_response = client.post(
        urljoin(configuration_endpoint, "response/{0}".format(rule_id)),
        json=serialized_response,
        )
    assert http_response.status_code == 200, "Can't set a response"

    assert client.get(base_endpoint).status_code == 404, "Wrong status code"
