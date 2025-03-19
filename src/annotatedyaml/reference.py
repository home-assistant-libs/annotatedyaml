from __future__ import annotations

from typing import TYPE_CHECKING

import yaml

from .objects import NodeDictClass, NodeListClass, NodeStrClass

if TYPE_CHECKING:
    from .loader import LoaderType


def _add_reference_to_node_class(
    obj: NodeDictClass | NodeListClass | NodeStrClass,
    loader: LoaderType,
    node: yaml.nodes.Node,
) -> None:
    """Add file reference information to a node class object."""
    obj.__config_file__ = loader.get_name
    if (start_mark := node.start_mark) is not None:
        obj.__line__ = start_mark.line + 1
