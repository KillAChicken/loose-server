"""Default client rules."""

from looseserver.client.rule import ClientRule
from looseserver.common.rule import RuleFactory
from looseserver.default.common.constants import RuleType
from looseserver.default.common.configuration import RuleFactoryPreparator


class PathRule(ClientRule):
    """Rule to match requests by path."""

    def __init__(self, path, rule_type=RuleType.PATH.name, rule_id=None):
        super(PathRule, self).__init__(rule_type, rule_id)
        self._path = path

    @property
    def path(self):
        """Path to match."""
        return self._path

    def __repr__(self):
        return "{class_name}('{path}')".format(class_name=self.__class__.__name__, path=self._path)


class MethodRule(ClientRule):
    """Rule to match requests by method."""

    def __init__(self, method, rule_type=RuleType.METHOD.name, rule_id=None):
        super(MethodRule, self).__init__(rule_type, rule_id)
        self._method = method.upper()

    @property
    def method(self):
        """Method to match."""
        return self._method

    def __repr__(self):
        return "{class_name}('{method}')".format(
            class_name=self.__class__.__name__,
            method=self._method,
            )


class CompositeRule(ClientRule):
    """Composite rule to match request by several rules simultaneously."""

    def __init__(self, children, rule_type=RuleType.COMPOSITE.name, rule_id=None):
        super(CompositeRule, self).__init__(rule_type, rule_id)
        self._children = tuple(children)

    @property
    def children(self):
        """Child rules."""
        return tuple(self._children)

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

    client_factory_preparator = RuleFactoryPreparator(rule_factory=rule_factory)
    client_factory_preparator.prepare_path_rule(path_rule_class=PathRule, base_url=base_url)
    client_factory_preparator.prepare_method_rule(method_rule_class=MethodRule)
    client_factory_preparator.prepare_composite_rule(composite_rule_class=CompositeRule)

    return rule_factory
