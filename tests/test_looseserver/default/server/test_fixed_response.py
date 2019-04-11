"""Test cases for FixedResponse."""

from urllib.parse import urljoin

import pytest

from looseserver.server.application import configure_application
from looseserver.default.common.constants import ResponseType
from looseserver.default.common.configuration import ResponseFactoryPreparator
from looseserver.default.server.response import FixedResponse


def test_response_representation():
    """Check the representation of the fixed response.

    1. Create a fixed response.
    2. Check result of the repr function.
    """
    status = 200
    headers = {"key": "value"}
    body = "body"
    response = FixedResponse(
        response_type=ResponseType.FIXED.name,
        status=status,
        headers=headers,
        body=body,
        )
    assert repr(response) == "FixedResponse()", "Wrong representation"


class TestParameters:
    """Test cases for fixed response parameters."""

    @pytest.fixture(autouse=True)
    def _setup(
            self,
            base_endpoint,
            configuration_endpoint,
            rule_factory,
            response_factory,
            rule_match_all,
        ):
        # pylint: disable=too-many-arguments,attribute-defined-outside-init
        self.__base_endpoint = base_endpoint
        self.__configuration_endpoint = configuration_endpoint
        self.__rule_factory = rule_factory
        self.__response_factory = response_factory
        self.__rule_match_all = rule_match_all

        preparator = ResponseFactoryPreparator(response_factory)
        preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

        application = configure_application(
            base_endpoint=self.__base_endpoint,
            configuration_endpoint=self.__configuration_endpoint,
            rule_factory=rule_factory,
            response_factory=response_factory,
            )

        self.__application_client = application.test_client()

    def _create_rule(self):
        serialized_rule = self.__rule_factory.serialize_rule(rule=self.__rule_match_all)

        http_response = self.__application_client.post(
            urljoin(self.__configuration_endpoint, "rules"),
            json=serialized_rule,
            )
        assert http_response.status_code == 200, "Can't create a rule"
        return http_response.json["data"]["rule_id"]

    @pytest.mark.parametrize(
        argnames="status",
        argvalues=[200, 300, 400, 500],
        ids=["Success", "Redirect", "Bad Request", "Server Error"],
        )
    def test_status(self, status):
        """Check that status can be set by fixed respone.

        1. Create a rule.
        2. Make a POST-request to set a fixed response with specified status.
        3. Make a request to the base endpoint.
        4. Check status of the response.
        """
        response = FixedResponse(
            response_type=ResponseType.FIXED.name,
            status=status,
            headers={},
            body="",
            )
        serialized_response = self.__response_factory.serialize_response(response=response)

        rule_id = self._create_rule()
        http_response = self.__application_client.post(
            urljoin(self.__configuration_endpoint, "response/{0}".format(rule_id)),
            json=serialized_response,
            )
        assert http_response.status_code == 200, "Can't set a response"

        assert self.__application_client.get(self.__base_endpoint).status_code == status, (
            "Wrong status code"
            )

    @pytest.mark.parametrize(
        argnames="headers",
        argvalues=[
            {},
            {"key": "value"},
            {
                "first": "value",
                "second": "value",
                },
            ],
        ids=[
            "Empty headers",
            "Single header",
            "Several headers",
            ]
        )
    def test_headers(self, headers):
        """Check that headers can be set by fixed respone.

        1. Create a rule.
        2. Make a POST-request to set a fixed response with specified headers.
        3. Make a request to the base endpoint.
        4. Check that response contains specified headers.
        """
        response = FixedResponse(
            response_type=ResponseType.FIXED.name,
            status=200,
            headers=headers,
            body="",
            )
        serialized_response = self.__response_factory.serialize_response(response=response)

        rule_id = self._create_rule()
        http_response = self.__application_client.post(
            urljoin(self.__configuration_endpoint, "response/{0}".format(rule_id)),
            json=serialized_response,
            )
        assert http_response.status_code == 200, "Can't set a response"

        http_response = self.__application_client.get(self.__base_endpoint)

        assert set(headers.items()).issubset(http_response.headers.items()), "Headers were not set"

    @pytest.mark.parametrize(
        argnames="body",
        argvalues=["", "body"],
        ids=["Empty", "Non-empty"],
        )
    def test_string_body(self, body):
        """Check that body can be set by fixed respone.

        1. Create a rule.
        2. Make a POST-request to set a fixed response with the specified string body.
        3. Make a request to the base endpoint.
        4. Check that response contains specified headers.
        """
        response = FixedResponse(
            response_type=ResponseType.FIXED.name,
            status=200,
            headers={},
            body=body,
            )
        serialized_response = self.__response_factory.serialize_response(response=response)

        rule_id = self._create_rule()
        http_response = self.__application_client.post(
            urljoin(self.__configuration_endpoint, "response/{0}".format(rule_id)),
            json=serialized_response,
            )
        assert http_response.status_code == 200, "Can't set a response"

        assert self.__application_client.get(self.__base_endpoint).data == body.encode("utf8"), (
            "Wrong body"
            )

    @pytest.mark.parametrize(
        argnames="body",
        argvalues=[b"", b"body"],
        ids=["Empty", "Non-empty"],
        )
    def test_bytes_body(self, body):
        """Check that body can be set by fixed respone.

        1. Create a rule.
        2. Make a POST-request to set a fixed response with the specified bytes body.
        3. Make a request to the base endpoint.
        4. Check that response contains specified headers.
        """
        response = FixedResponse(
            response_type=ResponseType.FIXED.name,
            status=200,
            headers={},
            body=body,
            )
        serialized_response = self.__response_factory.serialize_response(response=response)

        rule_id = self._create_rule()
        http_response = self.__application_client.post(
            urljoin(self.__configuration_endpoint, "response/{0}".format(rule_id)),
            json=serialized_response,
            )
        assert http_response.status_code == 200, "Can't set a response"
        assert self.__application_client.get(self.__base_endpoint).data == body, "Wrong body"
