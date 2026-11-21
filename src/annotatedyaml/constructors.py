"""Constructors for the custom loader."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import yaml

from .objects import NodeDictClass, NodeStrClass
from .reference import _add_reference_to_node_class
from .reference_object import _add_reference

if TYPE_CHECKING:
    from .loader import JSON_TYPE, LoaderType

_LOGGER = logging.getLogger(__name__)


def _get_input_name(loader: LoaderType) -> str:
    """Return the stream name, or the loader name when that is empty."""
    return loader.get_stream_name or loader.get_name


def _handle_mapping_tag(
    loader: LoaderType, node: yaml.nodes.MappingNode
) -> NodeDictClass:
    """Load YAML mappings into an ordered dictionary to preserve key order."""
    loader.flatten_mapping(node)
    nodes = loader.construct_pairs(node)

    # Check first if length of dict is equal to the length of the nodes
    # This is a quick way to check if the keys are unique
    try:
        conv_dict = NodeDictClass(nodes)
    except TypeError:
        pass
    else:
        if len(conv_dict) == len(nodes):
            _add_reference_to_node_class(conv_dict, loader, node)
            return conv_dict

    seen: dict = {}
    for (key, _), (child_node, _) in zip(nodes, node.value, strict=False):
        line = child_node.start_mark.line

        try:
            hash(key)
        except TypeError as exc:
            raise yaml.MarkedYAMLError(
                context=f'invalid key: "{key}"',
                context_mark=yaml.Mark(
                    _get_input_name(loader),
                    0,
                    line,
                    -1,
                    None,
                    None,  # type: ignore[arg-type]
                ),
            ) from exc

        if key in seen:
            _LOGGER.warning(
                'YAML file %s contains duplicate key "%s". Check lines %d and %d',
                _get_input_name(loader),
                key,
                seen[key] + 1,
                line + 1,
            )
        seen[key] = line

    mapping = NodeDictClass(nodes)
    _add_reference_to_node_class(mapping, loader, node)
    return mapping


def _construct_seq(loader: LoaderType, node: yaml.nodes.Node) -> JSON_TYPE:
    """Add line number and file name to Load YAML sequence."""
    (obj,) = loader.construct_yaml_seq(node)
    return _add_reference(obj, loader, node)


def _handle_scalar_tag(
    loader: LoaderType, node: yaml.nodes.ScalarNode
) -> str | int | float | None:
    """Add line number and file name to Load YAML sequence."""
    obj = node.value
    if not isinstance(obj, str):
        return obj
    str_class = NodeStrClass(obj)
    _add_reference_to_node_class(str_class, loader, node)
    return str_class
