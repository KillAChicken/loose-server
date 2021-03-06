"""Test cases for http clients."""

import io

import requests
import requests.sessions
import pytest

from looseserver.common.api import APIError
from looseserver.client.http import HTTPClient


@pytest.fixture
def _redirect_requests(application_factory, monkeypatch):
    """Redirect requests to the application module."""
    application_client = application_factory().test_client()

    def _patched_request(session, method, url, json=None):
        # pylint: disable=unused-argument
        application_response = application_client.open(url, method=method, json=json)

        response = requests.Response()
        response.status_code = application_response.status_code
        response.headers.update(application_response.headers)
        response.raw = io.BytesIO(application_response.data)

        return response

    monkeypatch.setattr(requests.sessions.Session, "request", _patched_request)


@pytest.fixture
def _fail_requests(monkeypatch):
    """Fail requests."""
    def _patched_request(*args, **kwargs):
        # pylint: disable=unused-argument
        response = requests.Response()
        response.status_code = 400

        return response

    monkeypatch.setattr(requests.sessions.Session, "request", _patched_request)


def test_successful_request(
        _redirect_requests,
        configuration_endpoint,
        client_rule_factory,
        client_response_factory,
        registered_rule,
    ):
    """Check that http client can send a request and handle successful response.

    1. Create a rule with the client.
    2. Check the rule.
    """
    client = HTTPClient(
        configuration_url=configuration_endpoint,
        rule_factory=client_rule_factory,
        response_factory=client_response_factory,
        )

    created_rule = client.create_rule(rule=registered_rule)
    assert created_rule.rule_id is not None, "Rule ID has not been set"


def test_failed_request_api_error(
        _redirect_requests,
        configuration_endpoint,
        client_rule_factory,
        client_response_factory,
    ):
    """Check that http client can handle failed response with APIError.

    1. Try to get a non-existing rule with the client.
    2. Check that APIError is raised.
    """
    client = HTTPClient(
        configuration_url=configuration_endpoint,
        rule_factory=client_rule_factory,
        response_factory=client_response_factory,
        )

    with pytest.raises(APIError) as exception_info:
        client.get_rule(rule_id="FakeID")

    assert exception_info.value.description == "Failed to find rule with ID 'FakeID'", (
        "Wrong APIError is raised"
        )


def test_failed_request_http_error(
        _fail_requests,
        configuration_endpoint,
        client_rule_factory,
        client_response_factory,
    ):
    """Check that http client can handle failed response with HTTPError.

    1. Try to get a rule with the client from the non-existing server.
    2. Check that HTTPError is raised.
    """
    client = HTTPClient(
        configuration_url=configuration_endpoint,
        rule_factory=client_rule_factory,
        response_factory=client_response_factory,
        )

    with pytest.raises(requests.HTTPError):
        client.get_rule(rule_id="FakeID")
