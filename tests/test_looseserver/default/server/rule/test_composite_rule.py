"""Test cases for CompositeRule."""

from urllib.parse import urljoin

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


def test_match_found(base_endpoint, server_rule_factory, configured_application_client, apply_rule):
    """Check that CompositeRule is triggered when all child rules are triggered.

    1. Prepare path, method and composite rules in the rule factory.
    2. Create a composite rule and set successful response for it.
    3. Make a request of the specified type to the specified path.
    4. Check that the rule finds a match.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_path_rule(path_rule_class=PathRule, base_url=base_endpoint)
    preparator.prepare_method_rule(method_rule_class=MethodRule)
    preparator.prepare_composite_rule(composite_rule_class=CompositeRule)

    path = "test"
    method = "POST"

    composite_rule = CompositeRule(
        rule_type=RuleType.COMPOSITE.name,
        children=[
            PathRule(rule_type=RuleType.PATH.name, path=path),
            MethodRule(rule_type=RuleType.METHOD.name, method=method),
            ],
        )
    apply_rule(composite_rule)

    http_response = configured_application_client.open(urljoin(base_endpoint, path), method=method)
    assert http_response.status_code == 200, "Wrong status code"


def test_no_match(base_endpoint, server_rule_factory, configured_application_client, apply_rule):
    """Check that CompositeRule is not triggered if any of the child rules is not triggered.

    1. Prepare method and composite rules in the rule factory.
    2. Create a composite rule and set successful response for it.
    3. Make 2 requests of the specified types to the base endpoint.
    4. Check that the rule does not find a match.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_method_rule(method_rule_class=MethodRule)
    preparator.prepare_composite_rule(composite_rule_class=CompositeRule)

    first_rule = MethodRule(rule_type=RuleType.METHOD.name, method="GET")
    second_rule = MethodRule(rule_type=RuleType.METHOD.name, method="POST")

    composite_rule = CompositeRule(
        rule_type=RuleType.COMPOSITE.name,
        children=[first_rule, second_rule],
        )
    apply_rule(composite_rule)

    get_http_response = configured_application_client.get(base_endpoint)
    assert get_http_response.status_code == 404, "Wrong status code"

    post_http_response = configured_application_client.post(base_endpoint)
    assert post_http_response.status_code == 404, "Wrong status code"


def test_no_children(base_endpoint, server_rule_factory, configured_application_client, apply_rule):
    """Check that composite rule is not triggered without children.

    1. Prepare composite rule in the rule factory.
    2. Create a composite rule and set successful response for it.
    3. Make a request to the base endpoint.
    4. Check that the rule does not find a match.
    """
    preparator = RuleFactoryPreparator(server_rule_factory)
    preparator.prepare_composite_rule(composite_rule_class=CompositeRule)

    composite_rule = CompositeRule(rule_type=RuleType.COMPOSITE.name, children=())
    apply_rule(composite_rule)

    http_response = configured_application_client.get(base_endpoint)
    assert http_response.status_code == 404, "Wrong status code"
