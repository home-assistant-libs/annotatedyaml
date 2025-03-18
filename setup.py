"""Build optional cython modules."""

import logging
import os
from distutils.command.build_ext import build_ext
from typing import Any

import setuptools

try:
    from setuptools import Extension
except ImportError:
    from distutils.core import Extension


_LOGGER = logging.getLogger(__name__)

TO_CYTHONIZE = [
    "src/annotatedyaml/objects.py",
    "src/annotatedyaml/reference.py",
]

EXTENSIONS = [
    Extension(
        ext.removeprefix("src/").removesuffix(".py").replace("/", "."),
        [ext],
        language="c",
        extra_compile_args=["-O3", "-g0"],
    )
    for ext in TO_CYTHONIZE
]


class BuildExt(build_ext):
    """Build extension class."""

    def build_extensions(self) -> None:
        """Build extensions."""
        try:
            super().build_extensions()
        except Exception:
            _LOGGER.info("Failed to build cython extensions")


def _build(setup_kwargs: dict[str, Any]) -> None:
    setup_kwargs["exclude_package_data"] = {
        pkg: ["*.c"] for pkg in setup_kwargs.get("packages", [setup_kwargs["name"]])
    }
    if os.environ.get("SKIP_CYTHON"):
        return
    try:
        from Cython.Build import cythonize

        setup_kwargs.update(
            {
                "ext_modules": cythonize(
                    EXTENSIONS,
                    compiler_directives={"language_level": "3"},  # Python 3
                ),
                "cmdclass": {"build_ext": BuildExt},
            }
        )
    except Exception:
        if os.environ.get("REQUIRE_CYTHON"):
            raise


setup_kwargs = {"name": "annotatedyaml"}
_build(setup_kwargs)
setuptools.setup(**setup_kwargs)
