"""Test cases for FixedResponse."""

import pytest

from looseserver.default.common.constants import ResponseType
from looseserver.default.common.configuration import ResponseFactoryPreparator
from looseserver.default.client.rule import MethodRule
from looseserver.default.client.response import FixedResponse
from looseserver.server.application import configure_application
from looseserver.client.flask import FlaskClient


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


def test_default_response_type():
    """Check the default response type of the fixed response.

    1. Create a fixed response without specifying its type.
    2. Check the response type.
    """
    response = FixedResponse()
    assert response.response_type == ResponseType.FIXED.name, "Wrong response type"


def test_default_parameters():
    """Check the default values of the response.

    1. Create a fixed response without specifying anything.
    2. Check status.
    3. Check headers.
    4. Check body.
    """
    response = FixedResponse()
    assert response.status == 200, "Wrong status"
    assert response.headers == {}, "Wrong headers"
    assert response.body == "", "Wrong body"


class TestParameters:
    """Test cases for fixed response parameters."""

    @pytest.fixture(autouse=True)
    def _setup(self, base_endpoint, configuration_endpoint, response_factory):
        # pylint: disable=attribute-defined-outside-init
        self.__base_endpoint = base_endpoint

        application = configure_application(
            base_endpoint=base_endpoint,
            configuration_endpoint=configuration_endpoint,
            )

        preparator = ResponseFactoryPreparator(response_factory)
        preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

        self.__application_client = application.test_client()

        self.__client = FlaskClient(
            base_url=configuration_endpoint,
            response_factory=response_factory,
            application_client=self.__application_client,
            )

    def _create_rule(self):
        return self.__client.create_rule(rule=MethodRule(method="GET"))

    @pytest.mark.parametrize(argnames="status", argvalues=[200, 400], ids=["Success", "Failure"])
    def test_set_response_status(self, status):
        """Check that response status can be set.

        1. Create a rule.
        2. Set a fixed response with specified status for the rule.
        3. Check the status of the response.
        """
        rule = self._create_rule()

        fixed_response = FixedResponse(status=status)
        self.__client.set_response(rule_id=rule.rule_id, response=fixed_response)

        http_response = self.__application_client.get(self.__base_endpoint)
        assert http_response.status_code == status, "Wrong status code"

    @pytest.mark.parametrize(
        argnames="headers",
        argvalues=[
            {},
            {"Header": "Value"},
            {"First-Header": "First Value", "Second-Header": "Second Value"},
            ],
        ids=["Without headers", "Single header", "Several headers"],
        )
    def test_set_response_headers(self, headers):
        """Check that response headers can be set.

        1. Create a rule.
        2. Set a fixed response with specified headers for the rule.
        3. Check the headers of the response.
        """
        rule = self._create_rule()

        fixed_response = FixedResponse(headers=headers)
        self.__client.set_response(rule_id=rule.rule_id, response=fixed_response)

        http_response = self.__application_client.get(self.__base_endpoint)
        assert set(http_response.headers.items()).issuperset(headers.items()), (
            "Headers were not set"
            )

    @pytest.mark.parametrize(argnames="body", argvalues=["", "body"], ids=["Empty", "Non-empty"])
    def test_set_response_string_body(self, body):
        """Check that response body can be set as a string.

        1. Create a rule.
        2. Set a fixed response with specified body for the rule.
        3. Check the body of the response.
        """
        rule = self._create_rule()

        fixed_response = FixedResponse(body=body)
        self.__client.set_response(rule_id=rule.rule_id, response=fixed_response)

        http_response = self.__application_client.get(self.__base_endpoint)
        assert http_response.data == body.encode("utf8"), "Wrong body"

    @pytest.mark.parametrize(
        argnames="unicode_body,encoding",
        argvalues=[
            (u"", "utf-8"),
            (u"тело", "utf-8"),
            (u"тело", "cp1251"),
            ],
        ids=["Empty", "Non-empty utf8", "Non-empty cp1251"],
        )
    def test_set_response_bytes_body(self, unicode_body, encoding):
        """Check that response body can be set as a bytes object.

        1. Create a rule.
        2. Set a response with specified body for the rule.
        3. Check the body of the response.
        """
        rule = self._create_rule()

        body = unicode_body.encode(encoding)
        headers = {"Content-Type": "text/plain; charset={0}".format(encoding)}

        fixed_response = FixedResponse(headers=headers, body=body)
        self.__client.set_response(rule_id=rule.rule_id, response=fixed_response)

        http_response = self.__application_client.get(self.__base_endpoint)
        assert http_response.data.decode(encoding) == unicode_body, "Wrong body"
