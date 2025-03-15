# Uplink

[![PyPI Version](https://img.shields.io/pypi/v/uplink.svg)](https://pypi.python.org/pypi/uplink)
[![CI](https://img.shields.io/github/actions/workflow/status/prkumar/uplink/ci.yml?branch=master&logo=github&label=CI)](https://github.com/prkumar/uplink/actions?query=event%3Apush+branch%master+workflow%3ACI)
[![Coverage Status](https://img.shields.io/codecov/c/github/prkumar/uplink.svg)](https://codecov.io/gh/prkumar/uplink)
[![Code Climate](https://api.codeclimate.com/v1/badges/d5c5666134763ff1d6c0/maintainability)](https://codeclimate.com/github/prkumar/uplink/maintainability)
[![Documentation Status](https://readthedocs.org/projects/uplink/badge/?version=latest)](http://uplink.readthedocs.io/en/latest/?badge=latest)
[![GitHub Discussions](https://img.shields.io/github/discussions/prkumar/uplink.png)](https://github.com/prkumar/uplink/discussions)
[![Gitter](https://badges.gitter.im/python-uplink/Lobby.svg)](https://gitter.im/python-uplink/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

- Builds Reusable Objects for Consuming Web APIs.
- Works with **Requests**, **aiohttp**, and **Twisted**.
- Inspired by [Retrofit](http://square.github.io/retrofit/).

## A Quick Walkthrough, with GitHub API v3

Uplink turns your HTTP API into a Python class.

```python
from uplink import Consumer, get, Path, Query


class GitHub(Consumer):
    """A Python Client for the GitHub API."""

    @get("users/{user}/repos")
    def get_repos(self, user: Path, sort_by: Query("sort")):
        """Retrieves the user's public repositories."""
```

Build an instance to interact with the webservice.

```python
github = GitHub(base_url="https://api.github.com/")
```

Then, executing an HTTP request is as simply as invoking a method.

```python
repos = github.get_repos(user="octocat", sort_by="created")
```

The returned object is a friendly [`requests.Response`](http://docs.python-requests.org/en/master/api/#requests.Response):

```python
print(repos.json())
# Output: [{'id': 64778136, 'name': 'linguist', ...
```

For sending non-blocking requests, Uplink comes with support for [`aiohttp` and `twisted`](https://github.com/prkumar/uplink/tree/master/examples/async-requests).

Ready to launch your first API client with Uplink? Start with this [quick tutorial](https://uplink.readthedocs.io/en/latest/user/quickstart.html)!

## Features

- **Quickly Define Structured API Clients**
  - Use decorators and type hints to describe each HTTP request
  - JSON, URL-encoded, and multipart request body and file upload
  - URL parameter replacement, request headers, and query parameter support

- **Bring Your Own HTTP Library**
  - [Non-blocking I/O support](https://github.com/prkumar/uplink/tree/master/examples/async-requests) for Aiohttp and Twisted
  - [Supply your own session](https://uplink.readthedocs.io/en/latest/user/clients.html#swapping-out-the-default-http-session) (e.g., `requests.Session`) for greater control

- **Easy and Transparent Deserialization/Serialization**
  - Define [custom converters](https://uplink.readthedocs.io/en/latest/user/serialization.html#custom-json-deserialization) for your own objects
  - Support for [`marshmallow`](https://github.com/prkumar/uplink/tree/master/examples/marshmallow) schemas, [`pydantic`](https://pydantic-docs.helpmanual.io/) models, and [handling collections](https://uplink.readthedocs.io/en/latest/user/serialization.html#converting-collections) (e.g., list of Users)

- **Extendable**
  - Install optional plugins for additional features (e.g., [protobuf support](https://github.com/prkumar/uplink-protobuf))
  - Compose [custom response and error handling](https://uplink.readthedocs.io/en/latest/user/quickstart.html#response-and-error-handling) functions as middleware

- **Authentication**
  - Built-in support for [Basic Authentication](https://uplink.readthedocs.io/en/latest/user/auth.html#basic-authentication)
  - Use existing auth libraries for supported clients (e.g., [`requests-oauthlib`](https://github.com/requests/requests-oauthlib))

Uplink officially supports Python 2.7 and 3.5+.

**Note:** Python 2.7 support will be removed in v0.10.0.

## Installation

To install the latest stable release, you can use `pip` (or `pipenv`):

```bash
pip install -U uplink
```

If you are interested in the cutting-edge, preview the upcoming release with:

```bash
pip install https://github.com/prkumar/uplink/archive/master.zip
```

### Extra! Extra

Further, uplink has optional integrations and features. You can view a full list of available extras [here](https://uplink.readthedocs.io/en/latest/user/install.html#extras).

When installing Uplink with `pip`, you can select extras using the format:

```bash
pip install -U uplink[extra1, extra2, ..., extraN]
```

For instance, to install `aiohttp` and `marshmallow` support:

```bash
pip install -U uplink[aiohttp, marshmallow]
```

## User Testimonials

**Michael Kennedy** ([@mkennedy](https://twitter.com/mkennedy)), host of [Talk Python](https://twitter.com/TalkPython) and [Python Bytes](https://twitter.com/pythonbytes) podcasts-

> Of course our first reaction when consuming HTTP resources in Python is to reach for Requests. But for *structured* APIs, we often want more than ad-hoc calls to Requests. We want a client-side API for our apps. Uplink is the quickest and simplest way to build just that client-side API. Highly recommended.

**Or Carmi** ([@liiight](https://github.com/liiight)), [notifiers](https://github.com/notifiers/notifiers) maintainer-

> Uplink's intelligent usage of decorators and typing leverages the most pythonic features in an elegant and dynamic way. If you need to create an API abstraction layer, there is really no reason to look elsewhere.

## Documentation

Check out the library's documentation at <https://uplink.readthedocs.io/>.

For new users, a good place to start is this [quick tutorial](https://uplink.readthedocs.io/en/latest/user/quickstart.html).

## Community

Use the [Discussions](https://github.com/prkumar/uplink/discussions) tab on GitHub to join the conversation! Ask questions, provide feedback, and meet other users!

We're migrating our community from [Gitter](https://gitter.im/python-uplink/Lobby) to GitHub [Discussions](https://github.com/prkumar/uplink/discussions). Feel free to search our Gitter lobby for past questions and answers. However, to help us transition, please start new threads/posts in GitHub Discussions instead of Gitter.

## Contributing

Want to report a bug, request a feature, or contribute code to Uplink? Checkout the [Contribution Guide](https://github.com/prkumar/uplink/blob/master/CONTRIBUTING.md) for where to start.
Thank you for taking the time to improve an open source project 💜
