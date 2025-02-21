"""Benchmarks."""

import pathlib

from pytest_codspeed import BenchmarkFixture

from annotatedyaml import load_yaml

FIXTURE_PATH = pathlib.Path(__file__).parent.parent.joinpath("fixtures")


def test_simple_load(benchmark: BenchmarkFixture) -> None:
    """Test loading a simple YAML file."""
    yaml_str = FIXTURE_PATH.joinpath("simple_automations.yaml").read_text()

    @benchmark
    def _load_yaml() -> None:
        load_yaml(yaml_str)
