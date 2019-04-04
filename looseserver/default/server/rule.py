"""Default server rules."""

import logging
from urllib.parse import urlparse

from looseserver.server.rule import ServerRule
from looseserver.common.rule import RuleFactory
from looseserver.default.common.configuration import RuleFactoryPreparator


class PathRule(ServerRule):
    """Rule to match requests by path."""

    def __init__(self, rule_type, path):
        super(PathRule, self).__init__(rule_type)
        self._path = path

    @property
    def path(self):
        """Path to match."""
        return self._path

    def is_match_found(self, request):
        """Check if requested url matches the path of the rule.

        :param request: incoming :class:flask.Request.
        :returns: boolean if match is found.
        """
        logging.getLogger(__name__).debug("Check request with %s", self)
        return urlparse(request.base_url).path == self._path

    def __repr__(self):
        return "{class_name}('{path}')".format(class_name=self.__class__.__name__, path=self._path)


class MethodRule(ServerRule):
    """Rule to match requests by method."""

    def __init__(self, rule_type, method):
        super(MethodRule, self).__init__(rule_type)
        self._method = method.upper()

    @property
    def method(self):
        """Method to match."""
        return self._method

    def is_match_found(self, request):
        """Check if requested method matches the method of the rule.

        :param request: incoming :class:flask.Request.
        :returns: boolean if match is found.
        """
        logging.getLogger(__name__).debug("Check request with %s", self)
        return request.method == self._method

    def __repr__(self):
        return "{class_name}('{method}')".format(
            class_name=self.__class__.__name__,
            method=self._method,
            )


class CompositeRule(ServerRule):
    """Composite rule to match request by several rules simultaneously."""

    def __init__(self, rule_type, children):
        super(CompositeRule, self).__init__(rule_type)
        self._children = tuple(children)

    @property
    def children(self):
        """Child rules."""
        return tuple(self._children)

    def is_match_found(self, request):
        """Check if request matches all the children rules.

        :param request: incoming :class:flask.Request.
        :returns: boolean if match is found.
        """
        logging.getLogger(__name__).debug("Check request with %s", self)
        if not self._children:
            return False

        return all(child.is_match_found(request) for child in self._children)

    def __repr__(self):
        return "{class_name}(children={children})".format(
            class_name=self.__class__.__name__,
            children=self._children,
            )


def create_rule_factory(base_url):
    """Create and prepare rule factory.

    :param base_url: base url for dynamically configured routes.
    :returns: instance of :class:`RuleFactory <looseserver.common.rule.RuleFactory>`.
    """
    rule_factory = RuleFactory()

    server_factory_preparator = RuleFactoryPreparator(rule_factory=rule_factory)
    server_factory_preparator.prepare_path_rule(path_rule_class=PathRule, base_url=base_url)
    server_factory_preparator.prepare_method_rule(method_rule_class=MethodRule)
    server_factory_preparator.prepare_composite_rule(composite_rule_class=CompositeRule)

    return rule_factory
