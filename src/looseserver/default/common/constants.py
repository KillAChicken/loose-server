"""Module with constants of the default configuration."""

import enum


class RuleType(enum.Enum):
    """Default rule types."""
    PATH = "path"
    METHOD = "method"
    COMPOSITE = "composite"


class ResponseType(enum.Enum):
    """Default response types."""
    FIXED = "fixed"
