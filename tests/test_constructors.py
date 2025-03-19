from __future__ import annotations

import io
from unittest.mock import Mock

from yaml.nodes import ScalarNode

from annotatedyaml.constructors import _handle_scalar_tag
from annotatedyaml.loader import PythonSafeLoader
from annotatedyaml.objects import NodeStrClass


def test__handle_scalar_tag_non_str():
    """Test _handle_scalar_tag with a non-str scalar."""
    loader = PythonSafeLoader(io.BytesIO(b""))
    node = ScalarNode("tag:yaml.org,2002:int", 123)
    node_str_class = _handle_scalar_tag(loader, node)
    assert not isinstance(node_str_class, NodeStrClass)
    assert node_str_class == 123


def test__handle_scalar_tag_str():
    """Test _handle_scalar_tag with a str scalar."""
    loader = PythonSafeLoader(io.BytesIO(b""))
    node = ScalarNode("tag:yaml.org,2002:str", "123", Mock(line=3))
    node_str_class = _handle_scalar_tag(loader, node)
    assert isinstance(node_str_class, NodeStrClass)
    assert node_str_class == "123"
    assert node_str_class.__config_file__ == "<file>"
    assert node_str_class.__line__ == node.start_mark.line + 1


def test__handle_scalar_tag_str_missing_startmark():
    """Test _handle_scalar_tag with a str scalar with no startmark."""
    loader = PythonSafeLoader(io.BytesIO(b""))
    node = ScalarNode("tag:yaml.org,2002:str", "123")
    node_str_class = _handle_scalar_tag(loader, node)
    assert isinstance(node_str_class, NodeStrClass)
    assert node_str_class == "123"
    assert node_str_class.__config_file__ == "<file>"
    assert not hasattr(node_str_class, "__line__")
