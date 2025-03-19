from __future__ import annotations

from typing import TYPE_CHECKING, overload

import yaml

from .objects import NodeDictClass, NodeListClass, NodeStrClass
from .reference import _add_reference_to_node_class

if TYPE_CHECKING:
    from .loader import LoaderType


@overload
def _add_reference(
    obj: list | NodeListClass, loader: LoaderType, node: yaml.nodes.Node
) -> NodeListClass: ...


@overload
def _add_reference(
    obj: str | NodeStrClass, loader: LoaderType, node: yaml.nodes.Node
) -> NodeStrClass: ...


@overload
def _add_reference(
    obj: dict | NodeDictClass, loader: LoaderType, node: yaml.nodes.Node
) -> NodeDictClass: ...


def _add_reference(
    obj: dict | list | str | NodeDictClass | NodeListClass | NodeStrClass,
    loader: LoaderType,
    node: yaml.nodes.Node,
) -> NodeDictClass | NodeListClass | NodeStrClass:
    """Add file reference information to an object."""
    if isinstance(obj, list):
        obj = NodeListClass(obj)
    elif isinstance(obj, str):
        obj = NodeStrClass(obj)
    elif isinstance(obj, dict):
        obj = NodeDictClass(obj)
    else:
        return obj  # type: ignore[unreachable]
    _add_reference_to_node_class(obj, loader, node)
    return obj
