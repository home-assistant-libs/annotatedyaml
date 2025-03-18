from __future__ import annotations

from typing import TYPE_CHECKING

import yaml

from .objects import NodeDictClass, NodeListClass, NodeStrClass

if TYPE_CHECKING:
    from .loader import LoaderType


def _add_reference_to_node_dict_class(
    obj: NodeDictClass,
    loader: LoaderType,
    node: yaml.nodes.Node,
) -> None:
    """Add file reference information to a node class object."""
    obj.__config_file__ = loader.get_name
    obj.__line__ = node.start_mark.line + 1


def _add_reference_to_node_list_class(
    obj: NodeListClass,
    loader: LoaderType,
    node: yaml.nodes.Node,
) -> None:
    """Add file reference information to a node class object."""
    obj.__config_file__ = loader.get_name
    obj.__line__ = node.start_mark.line + 1


def _add_reference_to_node_str_class(
    obj: NodeStrClass,
    loader: LoaderType,
    node: yaml.nodes.Node,
) -> None:
    """Add file reference information to a node class object."""
    obj.__config_file__ = loader.get_name
    obj.__line__ = node.start_mark.line + 1
