"""Test cases for abstract looseserver client."""

import uuid
from urllib.parse import urljoin

from looseserver.client.abstract import AbstractClient
from looseserver.client.rule import ClientRule
from looseserver.client.response import ClientResponse


def test_create_rule(rule_factory):
    """Check request data that client uses to create a rule.

    1. Create a rule factory.
    2. Create a subclass of the abstract client.
    3. Implement send request so that it checks the request parameters.
    4. Invoke the create_rule method.
    5. Check the rule, returned by the method call.
    """
    rule = ClientRule(rule_type="test")
    rule_factory.register_rule(
        rule_type=rule.rule_type,
        parser=lambda *args, **kwargs: ClientRule(rule_type=rule.rule_type),
        serializer=lambda *args, **kwargs: {}
        )
    rule_id = str(uuid.uuid4())

    class _Client(AbstractClient):
        def _send_request(self, url, method="GET", json=None):
            serialized_rule = self._rule_factory.serialize_rule(rule=rule)

            assert url == "rules", "Wrong url"
            assert method == "POST", "Wrong method"
            assert json == serialized_rule, "Wrong rule data"

            response_json = {"rule_id": rule_id}
            response_json.update(serialized_rule)
            return response_json

    client = _Client(base_url="/", rule_factory=rule_factory)
    created_rule = client.create_rule(rule=rule)
    assert created_rule.rule_id == rule_id, "Rule ID has not been set"


def test_get_rule(rule_factory):
    """Check request data that client uses to get a rule.

    1. Create a rule factory.
    2. Create a subclass of the abstract client.
    3. Implement send request so that it checks the request parameters.
    4. Invoke the get_rule method.
    5. Check the rule, returned by the method call.
    """
    rule = ClientRule(rule_type="test")
    rule_factory.register_rule(
        rule_type=rule.rule_type,
        parser=lambda *args, **kwargs: ClientRule(rule_type=rule.rule_type),
        serializer=lambda *args, **kwargs: {}
        )
    rule_id = str(uuid.uuid4())

    class _Client(AbstractClient):
        def _send_request(self, url, method="GET", json=None):
            assert url == "rule/{0}".format(rule_id), "Wrong url"
            assert method == "GET", "Wrong method"
            assert json is None, "Data has been specified"

            response_json = {"rule_id": rule_id}
            response_json.update(self._rule_factory.serialize_rule(rule=rule))
            return response_json

    client = _Client(base_url="/", rule_factory=rule_factory)
    obtained_rule = client.get_rule(rule_id=rule_id)
    assert obtained_rule.rule_id == rule_id, "Rule ID has not been set"


def test_set_response(response_factory):
    """Check request data that client uses to set a response.

    1. Create a response factory.
    2. Create a subclass of the abstract client.
    3. Implement send request so that it checks the request parameters.
    4. Invoke the set_response method.
    5. Check the response, returned by the method call.
    """
    response = ClientResponse(response_type="test")
    response_factory.register_response(
        response_type=response.response_type,
        parser=lambda *args, **kwargs: response,
        serializer=lambda *args, **kwargs: {}
        )
    rule_id = str(uuid.uuid4())

    class _Client(AbstractClient):
        def _send_request(self, url, method="GET", json=None):
            serialized_response = self._response_factory.serialize_response(response=response)

            assert url == "response/{0}".format(rule_id), "Wrong url"
            assert method == "POST", "Wrong method"
            assert json == serialized_response, "Wrong response data"

            return serialized_response

    client = _Client(base_url="/", response_factory=response_factory)
    assert client.set_response(rule_id=rule_id, response=response) is response, (
        "Response is not returned"
        )


def test_build_url():
    """Check method to build url.

    1. Create a subclass of the abstract client.
    2. Build url.
    3. Check the built url.
    """
    class _Client(AbstractClient):
        def _send_request(self, url, method="GET", json=None):
            pass

        def exposed_build_url(self, relative_url):
            """Expose 'protected' _build_url method."""
            return self._build_url(relative_url=relative_url)

    configuration_endpoint = "/config/"
    client = _Client(base_url=configuration_endpoint)

    relative_path = "test"
    expected_url = urljoin(configuration_endpoint, relative_path)
    assert client.exposed_build_url(relative_path) == expected_url, "Wrong url"
