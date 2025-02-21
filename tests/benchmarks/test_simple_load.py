"""Benchmarks."""

import pathlib

from pytest_codspeed import BenchmarkFixture

from annotatedyaml import parse_yaml

FIXTURE_PATH = pathlib.Path(__file__).parent.parent.joinpath("fixtures")


def test_simple_parse_yaml(benchmark: BenchmarkFixture) -> None:
    """Test parsing a simple YAML file."""
    yaml_str = FIXTURE_PATH.joinpath("simple_automations.yaml").read_text()

    @benchmark
    def _parse_yaml() -> None:
        parse_yaml(yaml_str)


def test_large_parse_yaml(benchmark: BenchmarkFixture) -> None:
    """Test parsing a large YAML file."""
    yaml_str = FIXTURE_PATH.joinpath("large_automations.yaml").read_text()

    @benchmark
    def _parse_yaml() -> None:
        parse_yaml(yaml_str)
