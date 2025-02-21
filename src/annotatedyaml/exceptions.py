from __future__ import annotations


class YAMLException(Exception):
    """Base class for all YAML exceptions."""


class YamlTypeError(YAMLException):
    """Raised by load_yaml_dict if top level data is not a dict."""
