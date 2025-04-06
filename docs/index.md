# Uplink 📡

A Declarative HTTP Client for Python. Inspired by
[Retrofit](http://square.github.io/retrofit/).

[![Release](https://img.shields.io/github/release/prkumar/uplink/all.svg)](https://github.com/prkumar/uplink)
[![Python
Version](https://img.shields.io/pypi/pyversions/uplink.svg)](https://pypi.python.org/pypi/uplink)
[![License](https://img.shields.io/github/license/prkumar/uplink.svg)](https://github.com/prkumar/uplink/blob/master/LICENSE)
[![Codecov](https://img.shields.io/codecov/c/github/prkumar/uplink.svg)](https://codecov.io/gh/prkumar/uplink)
[![GitHub
Discussions](https://img.shields.io/github/discussions/prkumar/uplink.png)](https://github.com/prkumar/uplink/discussions)

!!! note
Uplink is in beta development. The public API is still evolving, but we
expect most changes to be backwards compatible at this point.

Uplink turns your HTTP API into a Python class.

``` python
from uplink import Consumer, get, Path, Query


class GitHub(Consumer):
    """A Python Client for the GitHub API."""

    @get("users/{user}/repos")
    def get_repos(self, user: Path, sort_by: Query("sort")):
       """Get user's public repositories."""
```

Build an instance to interact with the webservice.

``` python
github = GitHub(base_url="https://api.github.com/")
repos = github.get_repos("prkumar", sort_by="created")
```

Then, executing an HTTP request is as simply as invoking a method.

``` python
print(repos.json())
# Output: [{'id': 64778136, 'name': 'linguist', ...
```

For sending non-blocking requests, Uplink comes with support for
`aiohttp` and `twisted`
([example](https://github.com/prkumar/uplink/tree/master/examples/async-requests)).

## Features

-   **Quickly Define Structured API Clients**
    -   Use decorators and type hints to describe each HTTP request
    -   JSON, URL-encoded, and multipart request body and file upload
    -   URL parameter replacement, request headers, and query parameter
        support
-   **Bring Your Own HTTP Library**
    -   [Non-blocking I/O
        support](https://github.com/prkumar/uplink/tree/master/examples/async-requests)
        for Aiohttp and Twisted
    -   `Supply your own session <swap_default_http_client>` (e.g.,
        `requests.Session`) for greater control
-   **Easy and Transparent Deserialization/Serialization**
    -   Define `custom converters <custom_json_deserialization>` for
        your own objects
    -   Support for
        [`marshmallow`](https://github.com/prkumar/uplink/tree/master/examples/marshmallow)
        schemas and `handling collections <converting_collections>`
        (e.g., list of Users)
    -   Support for pydantic models and
        `handling collections <converting_collections>` (e.g., list of
        Repos)
-   **Extendable**
    -   Install optional plugins for additional features (e.g.,
        [protobuf support](https://github.com/prkumar/uplink-protobuf))
    -   Compose
        `custom response and error handling <custom response handler>`
        functions as middleware
-   **Authentication**
    -   Built-in support for
        `Basic Authentication <basic_authentication>`
    -   Use existing auth libraries for supported clients (e.g.,
        [`requests-oauthlib`](https://github.com/requests/requests-oauthlib))

Uplink officially supports Python 3.10+.

## User Testimonials

**Michael Kennedy** ([@mkennedy](https://twitter.com/mkennedy)), host of
[Talk Python](https://twitter.com/TalkPython) and [Python
Bytes](https://twitter.com/pythonbytes) podcasts-

> Of course our first reaction when consuming HTTP resources in Python
> is to reach for Requests. But for *structured* APIs, we often want
> more than ad-hoc calls to Requests. We want a client-side API for our
> apps. Uplink is the quickest and simplest way to build just that
> client-side API. Highly recommended.

**Or Carmi** ([@liiight](https://github.com/liiight)),
[notifiers](https://github.com/notifiers/notifiers) maintainer-

> Uplink's intelligent usage of decorators and typing leverages the most
> pythonic features in an elegant and dynamic way. If you need to create
> an API abstraction layer, there is really no reason to look elsewhere.

## Where to go from here

- [Quickstart](user/quickstart.md)
- [Installation](user/install.md)
- [Introduction](user/introduction.md)
