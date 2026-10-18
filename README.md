<!-- markdownlint-disable MD041 -->

[![PyPi](https://img.shields.io/pypi/v/url-unwrap?style=flat-square)](https://pypi.org/project/url-unwrap/)
[![CI](https://img.shields.io/github/actions/workflow/status/janheinrichmerker/url-unwrap/ci.yml?branch=main&style=flat-square)](https://github.com/janheinrichmerker/url-unwrap/actions/workflows/ci.yml)
[![Code coverage](https://img.shields.io/codecov/c/github/janheinrichmerker/url-unwrap?style=flat-square)](https://codecov.io/github/janheinrichmerker/url-unwrap/)
[![Maintenance](https://img.shields.io/maintenance/yes/2026?style=flat-square)](https://github.com/janheinrichmerker/url-unwrap/graphs/contributors)
[![Python](https://img.shields.io/pypi/pyversions/url-unwrap?style=flat-square)](https://pypi.org/project/url-unwrap/)
[![Issues](https://img.shields.io/github/issues/janheinrichmerker/url-unwrap?style=flat-square)](https://github.com/janheinrichmerker/url-unwrap/issues)
[![Commit activity](https://img.shields.io/github/commit-activity/m/janheinrichmerker/url-unwrap?style=flat-square)](https://github.com/janheinrichmerker/url-unwrap/commits)
[![Downloads](https://img.shields.io/pypi/dm/url-unwrap?style=flat-square)](https://pypi.org/project/url-unwrap/)
[![License](https://img.shields.io/github/license/janheinrichmerker/url-unwrap?style=flat-square)](LICENSE)

# 🔗 url-unwrap

> [!WARNING]
> This is an experimental package, currently not tested against production data.

Unwrap redirect links and remove tracking parameters with the [ClearURLs](https://github.com/ClearURLs/Rules) rules.

## Installation

Install the package from PyPI:

```shell
pip install url-unwrap
```

## Usage

Unwrap a URL like this:

```python
from url_unwrap import unwrap

unwrap("https://www.google.com/url?q=https://example.org/a%3Fid%3D7%26utm_source%3Dx&sa=U")
# 'https://example.org/a?id=7'
```

Redirect links are followed until the target is reached, and tracking parameters (like `utm_source`) are removed along the way.
Besides the [ClearURLs](https://github.com/ClearURLs/Rules) rules, search result links from Google Images, Bing, and Yahoo are also unwrapped.

The ClearURLs rules are downloaded once and then shared.
To use a local copy of the rules instead, load them from a file:

```python
from url_unwrap import Providers, unwrap

providers = Providers.from_file("data.minify.json")
unwrap("https://example.org/?utm_source=x", providers)
# 'https://example.org/'
```

## Development

To build this package and contribute to its development you need to install the `build`, `setuptools` and `wheel` packages:

```shell
pip install build setuptools wheel
```

(On most systems, these packages are already pre-installed.)

Then, install the package and test dependencies:

```shell
pip install -e .[tests]
```

You can now verify your changes against the test suite.

```shell
ruff check .  # Code format and LINT
mypy .        # Static typing
pytest .      # Unit tests
```

Please also add tests for your newly developed code.

### Build wheels

Wheels for this package can be built with:

```shell
python -m build
```

## Support

If you hit any problems using this package, please file an [issue](https://github.com/janheinrichmerker/url-unwrap/issues/new).
We're happy to help!

## License

This repository is released under the [MIT license](LICENSE).
The ClearURLs rules are released under the [LGPL-3.0 license](https://github.com/ClearURLs/Rules/blob/master/LICENSE) and are downloaded, not bundled.
