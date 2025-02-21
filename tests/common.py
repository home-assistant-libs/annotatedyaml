"""Common test utilities."""

import logging
import os
import pathlib
from io import StringIO
from types import FrameType
from typing import Any, LiteralString
from unittest.mock import Mock, patch

from annotatedyaml import loader as yaml_loader

_LOGGER = logging.getLogger(__name__)
YAML_CONFIG_FILE = "test.yaml"


def get_test_config_dir(*add_path: Any) -> LiteralString | str | bytes:
    """Return a path to a test config dir."""
    return os.path.join(os.path.dirname(__file__), "testing_config", *add_path)


def patch_yaml_files(files_dict, endswith=True) -> Any:
    """Patch load_yaml with a dictionary of yaml files."""
    # match using endswith, start search with longest string
    matchlist = sorted(files_dict.keys(), key=len) if endswith else []

    def mock_open_f(fname: str | pathlib.Path, **_: Any) -> StringIO:
        """Mock open() in the yaml module, used by load_yaml."""
        # Return the mocked file on full match
        if isinstance(fname, pathlib.Path):
            fname = str(fname)

        if fname in files_dict:
            _LOGGER.debug("patch_yaml_files match %s", fname)
            res = StringIO(files_dict[fname])
            res.name = fname
            return res

        # Match using endswith
        for ends in matchlist:
            if fname.endswith(ends):
                _LOGGER.debug("patch_yaml_files end match %s: %s", ends, fname)
                res = StringIO(files_dict[ends])
                res.name = fname
                return res

        # Not found
        msg = f"File not found: {fname}"
        raise FileNotFoundError(msg)

    return patch.object(yaml_loader, "open", mock_open_f, create=True)
