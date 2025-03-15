# How to Contribute to Uplink

The following is a guide for contributing to Uplink. Thanks for taking the time to improve an open source project!

This guide is a work in progress. So, if you have suggestions for improving the contributors' experience, the release process, or really anything concerning the source code's management, please feel free to contact [@prkumar](https://github.com/prkumar) directly.

## Reporting Bugs and Making Feature Requests

We use the GitHub issue tracker for wrangling bug reports and feature requests. Before you open an issue, please do a quick search against both **closed and open** issues to ensure that the defect or feature request has not been previously reported or addressed.

We use GitHub milestones to associate approved features and verified defects to their respective target release versions (e.g., `v1.0.0` or `v0.x`). Also, we use GitHub projects to group issues by long-term enhancement efforts. (e.g., Support asynchronous requests).

### Feature Requests

As we're in initial development, the project is accepting feature requests! To request a feature, open a GitHub issue, summarize the enhancement, and add the **feature request** label.

## Installation

Install all development dependencies using:

```bash
pipenv install --dev
pipenv run pre-commit install
```

If you are unfamiliar with [pipenv](https://docs.pipenv.org/) but are comfortable with [virtualenvs](https://virtualenv.pypa.io/en/stable/), you can alternatively run `pip install pipenv` inside the virtualenv you are already using then invoke the commands from above. This will setup your virtualenv correctly.

Before submitting a pull request, run all tests with [tox](https://tox.readthedocs.io/en/latest/):

```bash
tox
```

## Making Changes to the Source

To find a feature or bug to work on, checkout the open GitHub issues with the label ["help wanted"](https://github.com/prkumar/uplink/labels/help%20wanted). Once you have found an issue that you'd like to work on, add a comment to the issue expressing your interest in developing the feature or fixing the bug, and mention [@prkumar](https://github.com/prkumar) in your comment.

Moreover, changes to the source code typically address one of the following:

* [Feature enhancement or minor bug fix](#feature-enhancement-or-minor-bug-fix)
* [Critical bug fix](#critical-bug-fix)

And, their development typically follows this workflow:

1. Fork the repository if you don't have write-access.
2. Make your changes, adhering to the [style guide](#style-guide).
3. Add or update [tests](#tests).
4. Update documentation, if necessary.
5. Add yourself to the `authors` list in `pyproject.toml`.
6. When your changes are ready for review, open a [pull request](#pull-request).
7. Merge changes.

## Development Process

In this section, we'll outline the various development stages of Uplink. And, as the development process and branching model go hand-in-hand, we'll also cover how our branching workflow ties into each stage.

To start off, let's address the two, everlasting branches: `stable` and `master`.

### `stable`

As the production branch, this branch should be the most stable branch. Nominally, `stable` strictly contains merge commits, each tagged with a release version (e.g, `v0.1.0`). See [releases](#releases) for more on how we handle the releasing process.

### `master`

This branch contains work-in-progress for the next immediate release.

### Feature Enhancement or Minor Bug Fix

Subject to inclusion in some future release, features are logically cohesive units of work that add value to Uplink. In like manner, fixing a minor bug adds value by addressing a value destroying characteristic of the code, a defect.

Further, a minor bug is a defect that we can wait to patch in a coming minor or major release. A defect that requires immediate attention needs a [critical bug fix](#critical-bug-fix).

Development of a feature or a minor bug fix should happen on a feature branch, which contains work for the next or some distant release. To start a feature branch, branch off of `master`. Preferably, prefix the branch name with `feature/` (or `feature/v{version}/`, where {version} is the feature's target release version -- e.g., `feature/v1.0.0/*`) for clarity. Make your changes on this branch, then when ready to merge, open a [pull request](#pull-request) against `master`.

Importantly, if your changes are not targeted for the next immediate release, keep them on the feature branch until `master` is bumped to the target version. However, you may open a pull request beforehand.

Also, after we have merged your changes into `master`, you should delete your feature branch, to keep the Git repository uncluttered.

### Critical Bug Fix

Critical bugs are defects affecting the latest released version of Uplink and require immediate action (i.e., we can't wait and patch the defect in a coming major or minor release). We assign the label ["critical"](https://github.com/prkumar/uplink/labels/critical) to GitHub issues tracking critical bugs.

To address a critical bug, we need to:

1. Create a hotfix branch off `stable`.
2. Increment the patch number.
3. Implement a fix.
4. Open [pull request](#pull-request) against `master`, and another against `stable`.

### Releases

Once we're ready to begin the release process, we'll create a release branch off an appropriate commit of `master`. The name of a release branch should follow the pattern `release/v{version}`, where `{version}` is the target release version number (e.g., `release/v1.0.0`).

Once the release branch is merged into `stable`, we consider the release completed. However, up until this point, we can make necessary changes to the release branch, while normal feature development continues on `master`.

When merging the release branch into `stable`, perform an explicit, non fast-forward **merge**. Then, on the merge commit in `stable`, create a tag named `v{version}`, where `{version}` is the target release version number (e.g., `v1.0.0`). Tagging the commit prompts our CI pipeline to deploy the latest release to PyPI.

Notably, before removing a release branch, we'll need to merge the branch into `master` to incorporate commits made after the release branch was cut. Moreover, once a release branch is cut, we need to bump the version number on `master`.

## Pull Request

Depending on the type of change you are making, the branching model may require merging your work into one or two target branches (typically one is `master`). Be sure to open a pull request for each target branch.

1. Open a pull request (PR) to merge your forked branch, the **candidate**, into a **base** branch of this repository.
2. Add Raj (`prkumar`) as a reviewer.
3. If your PR fails the CI check, investigate the build log for cause of failure, address locally, and update the candidate branch. Repeat this step until the PR passes the CI check.
4. If your PR fails the Codecov check, check the PR's Codecov report to identify modules experiencing a test coverage drop. Improve testing locally, then update the candidate branch.
5. Once all checks have passed and the assigned reviewers have approved, a maintainer will merge your pull requests into the base branch by selecting "Merge Pull Request" (i.e., a `--no-ff` merge).
6. If the CI build for the merge commit fails, you should revert the merge commit, address the issue locally, update the candidate branch, then revisit step 3.

## Tests

We use the unit testing framework `pytest`. Unit and integrations tests are kept under the `tests` directory, written in Python modules that match the filename pattern `test_*.py`.

Notably, the `conftest.py` files define several [pytest fixtures](https://docs.pytest.org/en/latest/fixture.html), for injecting a mock instance of an interface (defined in `uplink.interfaces`) or utility class (defined in `uplink.helpers`) into your tests.

### Writing an Integration Test

As a rule of thumb, an integration test should not exercise an actual API -- i.e., a mocked HTTP client should be used instead. This guideline facilitates efficient CI builds, produces side-effect free tests, and makes everyone happy 🤗.

To that end, the following pytest fixtures are available when writing integration tests:

#### `mock_client`

A fake HTTP client adapter that can be passed into the `client` constructor parameter of any `Consumer` subclass:

```python
api = MyConsumer(base_url=..., client=mock_client)
```

Further, this fixture keeps a `history` of "requests", which is helpful when we want to assert what the server should have received:

```python
api = MyConsumer(base_url=..., client=mock_client)

# Makes a "mocked" HTTP request
api.get_user("prkumar")

# Retrieve details of the above request
request = mock_client.history[-1]

assert "GET" == request.method, "The HTTP Method should be GET"
```

Check out the definition of `RequestInvocation` in `tests/integration/__init__.py` for the full set of exposed request attributes available for assertion.

At minimum, most integrations tests require the `mock_client` fixture.

#### `mock_response`

An HTTP response builder that can creates a fake response to be returned by `mock_client`:

```python
# Mock user response
mock_response.with_json({"id": 123, "username": "prkumar"})
mock_client.with_response(mock_response)

api = MyConsumer(base_url=..., client=mock_client)

# Verify user is returned
response = api.get_user("prkumar")
assert {"id": 123, "username": "prkumar"} == response.json()
```

## Style Guide

To maintain a consistent code style with the rest of Uplink, follow the [Google Python Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md).

Notably, we use a Sphinx plugin that can parse docstrings adherent to this style. Checkout [this page](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for examples of Google Python Style Guide docstrings.
