"""Module with configuration of the factories."""

from urllib.parse import urljoin

from looseserver.common.rule import RuleParseError, RuleSerializeError
from looseserver.common.response import ResponseParseError, ResponseSerializeError
from looseserver.default.common.constants import RuleType, ResponseType


class RuleFactoryPreparator:
    """Class to prepare rule factory."""

    def __init__(self, rule_factory):
        self._rule_factory = rule_factory

    def prepare_path_rule(self, path_rule_class, base_url):
        """Prepare path rule in the rule factory.

        :param path_rule_class: class of the path rule.
        :param base_url: base url for dynamically configured endpoints.
        """
        def _parser(rule_type, parameters):
            """Create path rule.

            :param rule_type: type of the rule.
            :param parameters: dictionary with parameters of the rule.
            :returns: instance of configured path rule class.
            """
            try:
                relative_path = parameters["path"]
            except (TypeError, KeyError) as error:
                message = "Rule parameters must be a dictionary with 'path' key"
                raise RuleParseError(message) from error

            path = urljoin(base_url, relative_path)
            return path_rule_class(rule_type=rule_type, path=path)

        def _serializer(rule_type, rule):
            # pylint: disable=unused-argument
            """Serialize path rule.

            :param rule_type: type of the rule.
            :param rule: path rule.
            :returns: dictionary with data.
            """
            try:
                path = rule.path
            except (TypeError, AttributeError) as error:
                raise RuleSerializeError("Path rule must have path attribute") from error

            return {
                "path": path,
                }

        self._rule_factory.register_rule(
            rule_type=RuleType.PATH.name,
            parser=_parser,
            serializer=_serializer,
            )

    def prepare_method_rule(self, method_rule_class):
        """Prepare method rule in the rule factory.

        :param method_rule_class: class of the method rule.
        """
        def _parser(rule_type, parameters):
            """Create method rule.

            :param rule_type: type of the rule.
            :param parameters: dictionary with parameters of the rule.
            :returns: instance of configured method rule class.
            """
            try:
                method = parameters["method"]
            except (TypeError, KeyError) as error:
                message = "Rule parameters must be a dictionary with 'method' key"
                raise RuleParseError(message) from error

            return method_rule_class(rule_type=rule_type, method=method)

        def _serializer(rule_type, rule):
            # pylint: disable=unused-argument
            """Serialize method rule.

            :param rule_type: type of the rule.
            :param rule: method rule.
            :returns: dictionary with data.
            """
            try:
                method = rule.method
            except (TypeError, AttributeError) as error:
                raise RuleSerializeError("Method rule must have method attribute") from error

            return {
                "method": method,
                }

        self._rule_factory.register_rule(
            rule_type=RuleType.METHOD.name,
            parser=_parser,
            serializer=_serializer,
            )

    def prepare_composite_rule(self, composite_rule_class):
        """Prepare composite rule in the rule factory.

        :param composite_rule_class: class of the composite rule.
        """
        def _parser(rule_type, parameters):
            """Create composite rule.

            :param rule_type: type of the rule.
            :param parameters: dictionary with parameters of the rule.
            :returns: instance of configured composite rule class.
            """
            try:
                children_data = parameters["children"]
            except (TypeError, KeyError) as error:
                message = "Rule parameters must be a dictionary with 'children' key"
                raise RuleParseError(message) from error

            children = [self._rule_factory.parse_rule(data) for data in children_data]

            return composite_rule_class(rule_type=rule_type, children=children)

        def _serializer(rule_type, rule):
            # pylint: disable=unused-argument
            """Serialize composite rule.

            :param rule_type: type of the rule.
            :param rule: composite rule.
            :returns: dictionary with data.
            """
            try:
                children = rule.children
            except (TypeError, AttributeError) as error:
                raise RuleSerializeError("Composite rule must have children attribute") from error

            children_data = [self._rule_factory.serialize_rule(rule) for rule in children]

            return {
                "children": children_data,
                }

        self._rule_factory.register_rule(
            rule_type=RuleType.COMPOSITE.name,
            parser=_parser,
            serializer=_serializer,
            )


class ResponseFactoryPreparator:
    """Class to prepare response factory."""

    def __init__(self, response_factory):
        self._response_factory = response_factory

    def prepare_fixed_response(self, fixed_response_class):
        """Prepare fixed response in the response factory.

        :param fixed_response_class: class of the fixed response.
        """
        def _parser(response_type, parameters):
            """Create fixed response.

            :param response_type: type of the response.
            :param parameters: dictionary with parameters of the rule.
            :returns: instance of configured composite rule class.
            """
            try:
                body = parameters["body"]
                status = parameters["status"]
                headers = parameters["headers"]
            except (TypeError, KeyError) as error:
                message = (
                    "Response parameters must be a dictionary with keys 'body', 'status', 'headers'"
                    )
                raise ResponseParseError(message) from error

            return fixed_response_class(
                response_type=response_type,
                body=body,
                status=status,
                headers=headers,
                )

        def _serializer(response_type, response):
            # pylint: disable=unused-argument
            """Serialize fixed response.

            :param response_type: type of the response.
            :param response: fixed response.
            :returns: dictionary with data.
            """
            try:
                body = response.body
                status = response.status
                headers = response.headers
            except (TypeError, AttributeError) as error:
                message = "Response must have attributes 'body', 'status' and 'headers'"
                raise ResponseSerializeError(message) from error

            return {
                "body": body,
                "status": status,
                "headers": headers,
                }

        self._response_factory.register_response(
            response_type=ResponseType.FIXED.name,
            parser=_parser,
            serializer=_serializer,
            )
