(usage)=

# Usage

Assuming that you've followed the {ref}`installations steps <installation>`, you're now ready to use this package.

Start by importing it:

```python
import annotatedyaml
```

TODO: Document usage

## Knowing which files a load used

`load_yaml`, `load_yaml_dict` and `parse_yaml` accept an optional, keyword-only
`loaded_paths` set. When one is given, every file that is opened and every
directory that an `!include_dir_*` tag consults is added to it:

```python
loaded_paths: set[str] = set()
config = annotatedyaml.load_yaml("configuration.yaml", loaded_paths=loaded_paths)
```

This is intended for callers that cache a loaded config and need to know when it
would change. Watching the paths in the set covers the whole include graph, at
any depth, without having to reimplement the include rules.

Some details worth knowing:

- **Directories are recorded as well as their files**, including a directory
  that does not exist yet. Adding or removing a file changes only the
  directory's own mtime, so the files alone are not enough to notice it.
- **Paths are normalised**, so the same file reached by different spellings
  (`a/../b.yaml` and `b.yaml`) appears once.
- **It does not depend on the loaded values.** Walking the result for
  `__config_file__` cannot see a file whose content is a bare scalar, because
  booleans, integers, floats and nulls have nowhere to carry an annotation.
- The parameter is **keyword-only**. Replacing `load_yaml` with a wrapper that
  takes a different third positional argument is a known pattern, and a
  silently mis-bound set would be worse than a clear error.
