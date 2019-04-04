"""Module to work with rules."""


class ClientRule:
    """Base class to manage a rule."""

    def __init__(self, rule_type, rule_id=None):
        self.rule_id = rule_id
        self._type = rule_type

    @property
    def rule_type(self):
        """Type of the rule."""
        return self._type
