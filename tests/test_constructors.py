from __future__ import annotations

from yaml.nodes import ScalarNode

from annotatedyaml.constructors import _handle_scalar_tag
from annotatedyaml.loader import PythonSafeLoader
from annotatedyaml.objects import NodeStrClass


def test__handle_scalar_tag_non_str():
    """Test _handle_scalar_tag with a non-str scalar."""
    loader = PythonSafeLoader()
    node = ScalarNode("tag:yaml.org,2002:int", 123)
    node_str_class = _handle_scalar_tag(loader, node)
    assert isinstance(node_str_class, NodeStrClass)
    assert node_str_class == "123"
    assert node_str_class.__config_file__ == "<string>"
    assert node_str_class.__line__ == node.start_mark.line + 1
