"""Configuration of pytest."""

import pytest

from looseserver.client.rule import ClientRule
from looseserver.client.response import ClientResponse
from looseserver.default.common.constants import RuleType, ResponseType
from looseserver.default.common.configuration import (
    RuleFactoryPreparator,
    ResponseFactoryPreparator,
    )


@pytest.fixture
def client_method_rule_class(client_rule_factory):
    """Class for client method rules."""
    class _MethodRule(ClientRule):
        # pylint: disable=too-few-public-methods
        def __init__(self, method, rule_type=RuleType.METHOD.name, rule_id=None):
            super(_MethodRule, self).__init__(rule_type=rule_type, rule_id=rule_id)
            self.method = method

    RuleFactoryPreparator(client_rule_factory).prepare_method_rule(method_rule_class=_MethodRule)

    return _MethodRule


@pytest.fixture
def client_fixed_response_class(client_response_factory):
    """Class for client fixed responses."""
    class _FixedResponse(ClientResponse):
        # pylint: disable=too-few-public-methods
        def __init__(
                self,
                status=200,
                headers=None,
                body="",
                response_type=ResponseType.FIXED.name,
            ):
            super(_FixedResponse, self).__init__(response_type=response_type)
            self.status = status
            self.headers = headers or {}
            self.body = body

    ResponseFactoryPreparator(client_response_factory).prepare_fixed_response(
        fixed_response_class=_FixedResponse,
        )

    return _FixedResponse
