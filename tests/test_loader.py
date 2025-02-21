"""Test annotatedyaml loader."""

import asyncio
import importlib
import io
import os
import pathlib
from collections.abc import Generator
from typing import Any
from unittest.mock import Mock, patch

import pytest
import voluptuous as vol
import yaml as pyyaml

import annotatedyaml as yaml_util
from annotatedyaml import YAMLException
from annotatedyaml import loader as yaml_loader
from tests.common import YAML_CONFIG_FILE


@pytest.fixture(params=["enable_c_loader", "disable_c_loader"])
def try_both_loaders(request: pytest.FixtureRequest) -> Generator[None]:
    """Disable the yaml c loader."""
    if request.param != "disable_c_loader":
        yield
        return
    try:
        cloader = pyyaml.CSafeLoader
    except ImportError:
        return
    del pyyaml.CSafeLoader
    importlib.reload(yaml_loader)
    yield
    pyyaml.CSafeLoader = cloader
    importlib.reload(yaml_loader)


@pytest.fixture(params=["enable_c_dumper", "disable_c_dumper"])
def try_both_dumpers(request: pytest.FixtureRequest) -> Generator[None]:
    """Disable the yaml c dumper."""
    if request.param != "disable_c_dumper":
        yield
        return
    try:
        cdumper = pyyaml.CSafeDumper
    except ImportError:
        return
    del pyyaml.CSafeDumper
    importlib.reload(yaml_loader)
    yield
    pyyaml.CSafeDumper = cdumper
    importlib.reload(yaml_loader)


@pytest.mark.usefixtures("try_both_loaders")
def test_simple_list() -> None:
    """Test simple list."""
    conf = "config:\n  - simple\n  - list"
    with io.StringIO(conf) as file:
        doc = yaml_loader.parse_yaml(file)
    assert doc["config"] == ["simple", "list"]


@pytest.mark.usefixtures("try_both_loaders")
def test_simple_dict() -> None:
    """Test simple dict."""
    conf = "key: value"
    with io.StringIO(conf) as file:
        doc = yaml_loader.parse_yaml(file)
    assert doc["key"] == "value"


@pytest.mark.parametrize("mock_yaml", ["message:\n  {{ states.state }}"])
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_unhashable_key(mock_yaml: None) -> None:
    """Test an unhashable key."""
    with pytest.raises(YAMLException):
        yaml_loader.load_yaml(YAML_CONFIG_FILE)


@pytest.mark.parametrize("mock_yaml", ["a: a\nnokeyhere"])
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_no_key(mock_yaml: None) -> None:
    """Test item without a key."""
    with pytest.raises(YAMLException):
        yaml_util.load_yaml(YAML_CONFIG_FILE)


@pytest.mark.usefixtures("try_both_loaders")
def test_environment_variable() -> None:
    """Test config file with environment variable."""
    os.environ["PASSWORD"] = "secret_password"  # noqa: S105
    conf = "password: !env_var PASSWORD"
    with io.StringIO(conf) as file:
        doc = yaml_loader.parse_yaml(file)
    assert doc["password"] == "secret_password"  # noqa: S105
    del os.environ["PASSWORD"]


@pytest.mark.usefixtures("try_both_loaders")
def test_environment_variable_default() -> None:
    """Test config file with default value for environment variable."""
    conf = "password: !env_var PASSWORD secret_password"
    with io.StringIO(conf) as file:
        doc = yaml_loader.parse_yaml(file)
    assert doc["password"] == "secret_password"  # noqa: S105


@pytest.mark.usefixtures("try_both_loaders")
def test_invalid_environment_variable() -> None:
    """Test config file with no environment variable sat."""
    conf = "password: !env_var PASSWORD"
    with pytest.raises(YAMLException), io.StringIO(conf) as file:
        yaml_loader.parse_yaml(file)


@pytest.mark.parametrize(
    ("mock_yaml_files", "value"),
    [
        ({"test.yaml": "value"}, "value"),
        ({"test.yaml": None}, {}),
        ({"test.yaml": "123"}, 123),
    ],
)
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_include_yaml(mock_yaml_files: None, value: Any) -> None:
    """Test include yaml."""
    conf = "key: !include test.yaml"
    with io.StringIO(conf) as file:
        doc = yaml_loader.parse_yaml(file)
        assert doc["key"] == value


@patch("annotatedyaml.loader.os.walk")
@pytest.mark.parametrize(
    ("mock_yaml_files", "value"),
    [
        ({"/test/one.yaml": "one", "/test/two.yaml": "two"}, ["one", "two"]),
        ({"/test/one.yaml": "1", "/test/two.yaml": "2"}, [1, 2]),
        ({"/test/one.yaml": "1", "/test/two.yaml": None}, [1]),
    ],
)
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_include_dir_list(mock_walk: Mock, mock_yaml_files: None, value: Any) -> None:
    """Test include dir list yaml."""
    mock_walk.return_value = [["/test", [], ["two.yaml", "one.yaml"]]]

    conf = "key: !include_dir_list /test"
    with io.StringIO(conf) as file:
        doc = yaml_loader.parse_yaml(file)
        assert sorted(doc["key"]) == sorted(value)


@patch("annotatedyaml.loader.os.walk")
@pytest.mark.parametrize(
    "mock_yaml_files",
    [
        {
            "/test/zero.yaml": "zero",
            "/test/tmp2/one.yaml": "one",
            "/test/tmp2/two.yaml": "two",
        }
    ],
)
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_include_dir_list_recursive(mock_walk: Mock, mock_yaml_files: None) -> None:
    """Test include dir recursive list yaml."""
    mock_walk.return_value = [
        ["/test", ["tmp2", ".ignore", "ignore"], ["zero.yaml"]],
        ["/test/tmp2", [], ["one.yaml", "two.yaml"]],
        ["/test/ignore", [], [".ignore.yaml"]],
    ]

    conf = "key: !include_dir_list /test"
    with io.StringIO(conf) as file:
        assert ".ignore" in mock_walk.return_value[0][1], "Expecting .ignore in here"
        doc = yaml_loader.parse_yaml(file)
        assert "tmp2" in mock_walk.return_value[0][1]
        assert ".ignore" not in mock_walk.return_value[0][1]
        assert sorted(doc["key"]) == sorted(["zero", "one", "two"])


@patch("annotatedyaml.loader.os.walk")
@pytest.mark.parametrize(
    ("mock_yaml_files", "value"),
    [
        (
            {"/test/first.yaml": "one", "/test/second.yaml": "two"},
            {"first": "one", "second": "two"},
        ),
        (
            {"/test/first.yaml": "1", "/test/second.yaml": "2"},
            {"first": 1, "second": 2},
        ),
        (
            {"/test/first.yaml": "1", "/test/second.yaml": None},
            {"first": 1, "second": {}},
        ),
    ],
)
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_include_dir_named(mock_walk: Mock, mock_yaml_files: None, value: Any) -> None:
    """Test include dir named yaml."""
    mock_walk.return_value = [
        ["/test", [], ["first.yaml", "second.yaml", "secrets.yaml"]]
    ]

    conf = "key: !include_dir_named /test"
    with io.StringIO(conf) as file:
        doc = yaml_loader.parse_yaml(file)
        assert doc["key"] == value


@patch("annotatedyaml.loader.os.walk")
@pytest.mark.parametrize(
    "mock_yaml_files",
    [
        {
            "/test/first.yaml": "one",
            "/test/tmp2/second.yaml": "two",
            "/test/tmp2/third.yaml": "three",
        }
    ],
)
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_include_dir_named_recursive(mock_walk: Mock, mock_yaml_files: None) -> None:
    """Test include dir named yaml."""
    mock_walk.return_value = [
        ["/test", ["tmp2", ".ignore", "ignore"], ["first.yaml"]],
        ["/test/tmp2", [], ["second.yaml", "third.yaml"]],
        ["/test/ignore", [], [".ignore.yaml"]],
    ]

    conf = "key: !include_dir_named /test"
    correct = {"first": "one", "second": "two", "third": "three"}
    with io.StringIO(conf) as file:
        assert ".ignore" in mock_walk.return_value[0][1], "Expecting .ignore in here"
        doc = yaml_loader.parse_yaml(file)
        assert "tmp2" in mock_walk.return_value[0][1]
        assert ".ignore" not in mock_walk.return_value[0][1]
        assert doc["key"] == correct


@patch("annotatedyaml.loader.os.walk")
@pytest.mark.parametrize(
    ("mock_yaml_files", "value"),
    [
        (
            {"/test/first.yaml": "- one", "/test/second.yaml": "- two\n- three"},
            ["one", "two", "three"],
        ),
        (
            {"/test/first.yaml": "- 1", "/test/second.yaml": "- 2\n- 3"},
            [1, 2, 3],
        ),
        (
            {"/test/first.yaml": "- 1", "/test/second.yaml": None},
            [1],
        ),
    ],
)
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_include_dir_merge_list(
    mock_walk: Mock, mock_yaml_files: None, value: Any
) -> None:
    """Test include dir merge list yaml."""
    mock_walk.return_value = [["/test", [], ["first.yaml", "second.yaml"]]]

    conf = "key: !include_dir_merge_list /test"
    with io.StringIO(conf) as file:
        doc = yaml_loader.parse_yaml(file)
        assert sorted(doc["key"]) == sorted(value)


@patch("annotatedyaml.loader.os.walk")
@pytest.mark.parametrize(
    "mock_yaml_files",
    [
        {
            "/test/first.yaml": "- one",
            "/test/tmp2/second.yaml": "- two",
            "/test/tmp2/third.yaml": "- three\n- four",
        }
    ],
)
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_include_dir_merge_list_recursive(
    mock_walk: Mock, mock_yaml_files: None
) -> None:
    """Test include dir merge list yaml."""
    mock_walk.return_value = [
        ["/test", ["tmp2", ".ignore", "ignore"], ["first.yaml"]],
        ["/test/tmp2", [], ["second.yaml", "third.yaml"]],
        ["/test/ignore", [], [".ignore.yaml"]],
    ]

    conf = "key: !include_dir_merge_list /test"
    with io.StringIO(conf) as file:
        assert ".ignore" in mock_walk.return_value[0][1], "Expecting .ignore in here"
        doc = yaml_loader.parse_yaml(file)
        assert "tmp2" in mock_walk.return_value[0][1]
        assert ".ignore" not in mock_walk.return_value[0][1]
        assert sorted(doc["key"]) == sorted(["one", "two", "three", "four"])


@patch("annotatedyaml.loader.os.walk")
@pytest.mark.parametrize(
    ("mock_yaml_files", "value"),
    [
        (
            {
                "/test/first.yaml": "key1: one",
                "/test/second.yaml": "key2: two\nkey3: three",
            },
            {"key1": "one", "key2": "two", "key3": "three"},
        ),
        (
            {
                "/test/first.yaml": "key1: 1",
                "/test/second.yaml": "key2: 2\nkey3: 3",
            },
            {"key1": 1, "key2": 2, "key3": 3},
        ),
        (
            {
                "/test/first.yaml": "key1: 1",
                "/test/second.yaml": None,
            },
            {"key1": 1},
        ),
    ],
)
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_include_dir_merge_named(
    mock_walk: Mock, mock_yaml_files: None, value: Any
) -> None:
    """Test include dir merge named yaml."""
    mock_walk.return_value = [["/test", [], ["first.yaml", "second.yaml"]]]

    conf = "key: !include_dir_merge_named /test"
    with io.StringIO(conf) as file:
        doc = yaml_loader.parse_yaml(file)
        assert doc["key"] == value


@patch("annotatedyaml.loader.os.walk")
@pytest.mark.parametrize(
    "mock_yaml_files",
    [
        {
            "/test/first.yaml": "key1: one",
            "/test/tmp2/second.yaml": "key2: two",
            "/test/tmp2/third.yaml": "key3: three\nkey4: four",
        }
    ],
)
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_include_dir_merge_named_recursive(
    mock_walk: Mock, mock_yaml_files: None
) -> None:
    """Test include dir merge named yaml."""
    mock_walk.return_value = [
        ["/test", ["tmp2", ".ignore", "ignore"], ["first.yaml"]],
        ["/test/tmp2", [], ["second.yaml", "third.yaml"]],
        ["/test/ignore", [], [".ignore.yaml"]],
    ]

    conf = "key: !include_dir_merge_named /test"
    with io.StringIO(conf) as file:
        assert ".ignore" in mock_walk.return_value[0][1], "Expecting .ignore in here"
        doc = yaml_loader.parse_yaml(file)
        assert "tmp2" in mock_walk.return_value[0][1]
        assert ".ignore" not in mock_walk.return_value[0][1]
        assert doc["key"] == {
            "key1": "one",
            "key2": "two",
            "key3": "three",
            "key4": "four",
        }


@patch("annotatedyaml.loader.open", create=True)
@pytest.mark.usefixtures("try_both_loaders")
def test_load_yaml_encoding_error(mock_open: Mock) -> None:
    """Test raising a UnicodeDecodeError."""
    mock_open.side_effect = UnicodeDecodeError("", b"", 1, 0, "")
    with pytest.raises(YAMLException):
        yaml_loader.load_yaml("test")


@pytest.mark.usefixtures("try_both_dumpers")
def test_dump() -> None:
    """The that the dump method returns empty None values."""
    assert yaml_util.dump({"a": None, "b": "b"}) == "a:\nb: b\n"


@pytest.mark.usefixtures("try_both_dumpers")
def test_dump_unicode() -> None:
    """The that the dump method returns empty None values."""
    assert yaml_util.dump({"a": None, "b": "привет"}) == "a:\nb: привет\n"


@pytest.mark.parametrize("mock_yaml", ['key: [1, "2", 3]'])
@pytest.mark.usefixtures("try_both_dumpers", "patch_yaml_config")
def test_representing_yaml_loaded_data(mock_yaml: None) -> None:
    """Test we can represent YAML loaded data."""
    data = yaml_loader.load_yaml(YAML_CONFIG_FILE)
    assert yaml_util.dump(data) == "key:\n- 1\n- '2'\n- 3\n"


@pytest.mark.parametrize("mock_yaml", ["key: thing1\nkey: thing2"])
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_duplicate_key(caplog: pytest.LogCaptureFixture, mock_yaml: None) -> None:
    """Test duplicate dict keys."""
    yaml_loader.load_yaml(YAML_CONFIG_FILE)
    assert "contains duplicate key" in caplog.text


@pytest.mark.parametrize(
    "mock_yaml_files",
    [{YAML_CONFIG_FILE: "key: !secret a", yaml_util.SECRET_YAML: "a: 1\nb: !secret a"}],
)
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_no_recursive_secrets(mock_yaml_files: None) -> None:
    """Test that loading of secrets from the secrets file fails correctly."""
    with pytest.raises(YAMLException) as e:
        yaml_loader.load_yaml(YAML_CONFIG_FILE)

    assert e.value.args == ("Secrets not supported in this YAML file",)


def test_input_class() -> None:
    """Test input class."""
    yaml_input = yaml_util.Input("hello")
    yaml_input2 = yaml_util.Input("hello")

    assert yaml_input.name == "hello"
    assert yaml_input == yaml_input2

    assert len({yaml_input, yaml_input2}) == 1


@pytest.mark.usefixtures("try_both_loaders", "try_both_dumpers")
def test_input() -> None:
    """Test loading inputs."""
    data = {"hello": yaml_util.Input("test_name")}
    assert yaml_util.parse_yaml(yaml_util.dump(data)) == data


@pytest.mark.skipif(
    not os.environ.get("HASS_CI"),
    reason="This test validates that the CI has the C loader available",
)
def test_c_loader_is_available_in_ci() -> None:
    """Verify we are testing the C loader in the CI."""
    assert yaml_util.loader.HAS_C_LOADER is True


@pytest.mark.usefixtures("try_both_loaders")
async def test_loading_actual_file_with_syntax_error() -> None:
    """Test loading a real file with syntax errors."""
    fixture_path = pathlib.Path(__file__).parent.joinpath("fixtures", "bad.yaml.txt")
    loop = asyncio.get_event_loop()

    with pytest.raises(YAMLException):
        await loop.run_in_executor(None, yaml_loader.load_yaml, fixture_path, None)


@pytest.mark.usefixtures("try_both_loaders")
def test_string_annotated() -> None:
    """Test strings are annotated with file + line."""
    conf = (
        "key1: str\n"
        "key2:\n"
        "  blah: blah\n"
        "key3:\n"
        " - 1\n"
        " - 2\n"
        " - 3\n"
        "key4: yes\n"
        "key5: 1\n"
        "key6: 1.0\n"
    )
    expected_annotations = {
        "key1": [("<file>", 1), ("<file>", 1)],
        "key2": [("<file>", 2), ("<file>", 3)],
        "key3": [("<file>", 4), ("<file>", 5)],
        "key4": [("<file>", 8), (None, None)],
        "key5": [("<file>", 9), (None, None)],
        "key6": [("<file>", 10), (None, None)],
    }
    with io.StringIO(conf) as file:
        doc = yaml_loader.parse_yaml(file)
    for key, value in doc.items():
        assert getattr(key, "__config_file__", None) == expected_annotations[key][0][0]
        assert getattr(key, "__line__", None) == expected_annotations[key][0][1]
        assert (
            getattr(value, "__config_file__", None) == expected_annotations[key][1][0]
        )
        assert getattr(value, "__line__", None) == expected_annotations[key][1][1]


@pytest.mark.usefixtures("try_both_loaders")
def test_string_used_as_vol_schema() -> None:
    """Test the subclassed strings can be used in voluptuous schemas."""
    conf = "wanted_data:\n  key_1: value_1\n  key_2: value_2\n"
    with io.StringIO(conf) as file:
        doc = yaml_loader.parse_yaml(file)

    # Test using the subclassed strings in a schema
    schema = vol.Schema(
        {vol.Required(key): value for key, value in doc["wanted_data"].items()},
    )
    # Test using the subclassed strings when validating a schema
    schema(doc["wanted_data"])
    schema({"key_1": "value_1", "key_2": "value_2"})
    with pytest.raises(vol.Invalid):
        schema({"key_1": "value_2", "key_2": "value_1"})


@pytest.mark.parametrize(
    ("mock_yaml", "expected_data"), [("", {}), ("bla:", {"bla": None})]
)
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_load_yaml_dict(mock_yaml: None, expected_data: Any) -> None:
    """Test item without a key."""
    assert yaml_util.load_yaml_dict(YAML_CONFIG_FILE) == expected_data


@pytest.mark.parametrize("mock_yaml", ["abc", "123", "[]"])
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_load_yaml_dict_fail(mock_yaml: None) -> None:
    """Test item without a key."""
    with pytest.raises(YAMLException):
        yaml_loader.load_yaml_dict(YAML_CONFIG_FILE)


@pytest.mark.parametrize(
    "tag",
    [
        "!include",
        "!include_dir_named",
        "!include_dir_merge_named",
        "!include_dir_list",
        "!include_dir_merge_list",
    ],
)
@pytest.mark.usefixtures("try_both_loaders")
def test_include_without_parameter(tag: str) -> None:
    """Test include extensions without parameters."""
    with (
        io.StringIO(f"key: {tag}") as file,
        pytest.raises(YAMLException, match=f"{tag} needs an argument"),
    ):
        yaml_loader.parse_yaml(file)


@pytest.mark.parametrize(
    ("open_exception", "load_yaml_exception"),
    [
        (FileNotFoundError, OSError),
        (NotADirectoryError, YAMLException),
        (PermissionError, YAMLException),
    ],
)
@pytest.mark.usefixtures("try_both_loaders")
def test_load_yaml_wrap_oserror(
    open_exception: Exception,
    load_yaml_exception: Exception,
) -> None:
    """Test load_yaml wraps OSError in AnnotatedYAMLOSError."""
    with (
        patch("annotatedyaml.loader.open", side_effect=open_exception),
        pytest.raises(load_yaml_exception),
    ):
        yaml_loader.load_yaml("bla")


@pytest.mark.parametrize("mock_yaml", ["key: !include missing.yaml"])
@pytest.mark.usefixtures("try_both_loaders", "patch_yaml_config")
def test_load_missing_included_file(mock_yaml: None) -> None:
    """Test loading a file that includes a missing file."""
    with pytest.raises(YAMLException):
        yaml_loader.load_yaml(YAML_CONFIG_FILE)
