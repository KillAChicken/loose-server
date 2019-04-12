"""Test cases for abstract looseserver client."""

import uuid
from urllib.parse import urljoin

from looseserver.client.abstract import AbstractClient


def test_create_rule(client_rule_factory, registered_rule):
    """Check request data that client uses to create a rule.

    1. Create a subclass of the abstract client.
    2. Implement send request so that it checks the request parameters.
    3. Invoke the create_rule method.
    4. Check the rule, returned by the method call.
    """
    rule_id = str(uuid.uuid4())

    class _Client(AbstractClient):
        def _send_request(self, url, method="GET", json=None):
            serialized_rule = self._rule_factory.serialize_rule(rule=registered_rule)

            assert url == "rules", "Wrong url"
            assert method == "POST", "Wrong method"
            assert json == serialized_rule, "Wrong rule data"

            response_json = {"rule_id": rule_id}
            response_json.update(serialized_rule)
            return response_json

    client = _Client(base_url="/", rule_factory=client_rule_factory)
    created_rule = client.create_rule(rule=registered_rule)
    assert created_rule.rule_id == rule_id, "Rule ID has not been set"


def test_get_rule(client_rule_factory, registered_rule):
    """Check request data that client uses to get a rule.

    1. Create a subclass of the abstract client.
    2. Implement send request so that it checks the request parameters.
    3. Invoke the get_rule method.
    4. Check the rule, returned by the method call.
    """
    rule_id = str(uuid.uuid4())

    class _Client(AbstractClient):
        def _send_request(self, url, method="GET", json=None):
            assert url == "rule/{0}".format(rule_id), "Wrong url"
            assert method == "GET", "Wrong method"
            assert json is None, "Data has been specified"

            response_json = {"rule_id": rule_id}
            response_json.update(self._rule_factory.serialize_rule(rule=registered_rule))
            return response_json

    client = _Client(base_url="/", rule_factory=client_rule_factory)
    obtained_rule = client.get_rule(rule_id=rule_id)
    assert obtained_rule.rule_id == rule_id, "Rule ID has not been set"


def test_delete_rule():
    """Check request data that client uses to remove a rule.

    1. Create a subclass of the abstract client.
    2. Implement send request so that it checks the request parameters.
    3. Invoke the remove_rule method.
    """
    rule_id = str(uuid.uuid4())

    class _Client(AbstractClient):
        def _send_request(self, url, method="GET", json=None):
            assert url == "rule/{0}".format(rule_id), "Wrong url"
            assert method == "DELETE", "Wrong method"
            assert json is None, "Data has been specified"

    client = _Client(base_url="/")
    client.remove_rule(rule_id=rule_id)


def test_set_response(client_response_factory, registered_response):
    """Check request data that client uses to set a response.

    1. Create a subclass of the abstract client.
    2. Implement send request so that it checks the request parameters.
    3. Invoke the set_response method.
    4. Check the response, returned by the method call.
    """
    rule_id = str(uuid.uuid4())

    class _Client(AbstractClient):
        def _send_request(self, url, method="GET", json=None):
            serialized_response = self._response_factory.serialize_response(registered_response)

            assert url == "response/{0}".format(rule_id), "Wrong url"
            assert method == "POST", "Wrong method"
            assert json == serialized_response, "Wrong response data"

            return serialized_response

    client = _Client(base_url="/", response_factory=client_response_factory)
    response = client.set_response(rule_id=rule_id, response=registered_response)
    assert response.response_type == registered_response.response_type, "Wrong response is returned"


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
