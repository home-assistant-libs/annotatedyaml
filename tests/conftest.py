"""Pytest configuration file for the tests package."""

from collections.abc import Generator

import pytest

from tests.common import YAML_CONFIG_FILE, patch_yaml_files


@pytest.fixture
def mock_yaml() -> str:
    """
    Fixture to parametrize the content of test yaml file.

    To set yaml content, tests can be marked with:
    @pytest.mark.parametrize("mock_yaml", ["..."])
    Add the `mock_yaml: None` fixture to the test.
    """
    return ""


@pytest.fixture
def mock_yaml_files(mock_yaml: str) -> dict[str, str]:
    """
    Fixture to parametrize multiple yaml configuration files.

    To set the YAML files to patch, tests can be marked with:
    @pytest.mark.parametrize(
        "mock_yaml_files", [{"configuration.yaml": "..."}]
    )
    Add the `mock_yaml_files: None` fixture to the test.
    """
    return {YAML_CONFIG_FILE: mock_yaml}


@pytest.fixture
def patch_yaml_config(mock_yaml_files: dict[str, str]) -> Generator[None]:
    """
    Fixture to mock the content of the yaml configuration files.

    Patches yaml configuration files using the `mock_yaml`
    and `mock_yaml_files` fixtures.
    """
    with patch_yaml_files(mock_yaml_files):
        yield
