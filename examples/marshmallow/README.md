# Response Deserialization with Marshmallow

Many modern Web APIs deliver content as JSON objects. To abstract away
the data source, we often want to convert that JSON into a regular
Python object, so that other parts of our code can interact with the
resource using well-defined methods and attributes.

This example illustrates how to use Uplink with
[`marshmallow`](https://marshmallow.readthedocs.io/en/latest/) to
have your JSON API return Python objects.


## Requirements

Uplink's integration with `marshmallow` is an optional feature. You
can either install `marshmallow` separately or declare the extra when
installing Uplink with ``pip``:

```
$ pip install -U uplink[marshmallow]
```

## Overview

This example includes three files:

- `schemas.py`: Defines our schemas for repositories and contributors.
- `github.py`: Defines a `GitHub` API with two methods:
    - `GitHub.get_repos`: Gets all public repositories. Uses the
        repository schema to return `Repo` objects.
    - `GitHub.get_contributors`: Lists contributors for the specified repository.
       Uses the contributors schema to return `Contributor` objects.
- `main.py`: Connects all the pieces with an example that prints to the
   console the contributors for the first 10 public repositories.

## Challenge
Using the [`async-requests`](../async-requests/) example
as a guide, rewrite `main.py` to make non-blocking requests using
either `aiohttp` or `twisted`.

