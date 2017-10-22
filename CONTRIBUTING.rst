How to Contribute to Uplink
***************************

The following is a guide for contributing to Uplink. Thanks for taking the
time and putting that work in!

Making changes to the source
============================

A unit of development typically looks like the following:

1. Fork the repository if you don't have write-access.
2. Make your changes, adhering to the `style guide`_.
3. Add or update tests_.
4. Update documentation, if necessary.
5. When your changes are ready for review, open a `pull request`_.
6. Merge and pat back.

Changes to the source code typically address one of the following:

* `Feature enhancement/non-critical bug fix`_
* `Critical bug fix`_

Development Process
===================

In this section, we'll outline the various development stages of Uplink.
Moreover, we use the GitFlow branching model for Uplink, and as the development
process and branching model go hand-in-hand, we'll cover how GitFlow ties into
each stage.

To start off, we'll cover the two, everlasting branches: ``master`` and
``develop``.

``master``
----------

This branch is the most stable branch. Nominally, ``master``
strictly contains merge commits, each tagged with a release version (e.g,
``v0.1.0``). See releases_ for more on how we handle the releasing
process.

You can read about the `master branch
<http://nviecom/posts/a-successful-git-branching -model/#the-main-branches>`_
in the linked GitFlow article.

``develop``
-----------

This branch contains work-in-progress for the next immediate release.
You can read about the `develop branch
<http://nviecom/posts/a-successful-git-branching -model/#the-main-branches>`_
in the linked GitFlow article..

Feature Enhancement/Non-Critical Bug Fix
----------------------------------------

Subject to inclusion in some future release, features are logically cohesive
units of work that add value to Uplink. In like manner, a
non-critical bug fix adds value in that it addresses a value destroying
characteristic of the code, a defect. Further, a non-critical bug is a
defect that we can wait to patch in a different version. A defect that
requires immediate attention needs a `critical bug fix`_.

Development of a feature or a non-critical bug fix should happen on a
feature branch, which contains work for the next or some distant
release. Feature development typically looks like:

1. Branch off of ``develop``. Preferably, prefix the branch name with
   ``feature/`` (or ``feature/v{version}/``, where {version} is the feature's
   target release version -- e.g., ``feature/v1.0.0/*``) for clarity.
2. Make your changes.
3. If your changes are not targeted for the next immediate release, keep them
   on the feature branch until the release branch is cut (see releases_).
4. Once you're done making changes, it's time to merge into develop:

 - Substantial changes require `opening a pull request`_.
 - Always **squash and merge**.

5. If the ``develop`` branch fails the Travis CI or Coveralls builds that run
   immediately after your feature merge, revert the squashed merge commit.
   Address the issue locally -- i.e., go back to step 2.
6. Delete the feature branch.

You can read more about `feature branches
<http://nvie.com/posts/a-successful-git-branching-model/#feature-branches>`_
in the linked GitFlow article.

Critical Bug Fix
----------------

To fix a critical bug that affects the latest released version of Uplink and
requires immediate action (i.e., we can't wait and fix it in the next
release), we'll need to:

1. Create a hotfix branch off ``master``.
2. Increment the version number.
3. Implement a fix.
4. Open `pull request`_ against ``develop``, and another against ``master``.

You can read more about `hotfix branches
<http://nvie.com/posts/a-successful-git-branching-model/#hotfix-branches>`_
in the linked GitFlow article.

Releases
--------

Once we're ready to begin the release process, we'll create a release branch
off an appropriate commit of ``develop``. The name of a release branch
should follow the pattern ``release/v{version}``, where ``{version}`` is the
target release version number (e.g., ``release/v1.0.0``).

Once the release branch is merged into ``master``, we consider the release
completed. However, up until this point, we can make necessary changes to
the release branch, while normal feature development continues on ``develop``.

When merging the release branch into ``master``, be sure to **squash and
merge**. After merging, create a tag named ``v{version}``, where
``{version}`` is the target release version number (e.g., ``v1.0.0``),
on the the merge commit in ``master``. Tagging the commit prompts Travis
CI to deploy the latest release to PyPI.

You can read more about `release branches
<http://nvie.com/posts/a-successful-git-branching-model/#release-branches>`_
in the linked GitFlow article. Notably, before removing a release branch, we'll
need to merge the branch into ``develop`` to incorporate commits made after the
release branch was cut. Moreover, once a release branch is cut, we need to bump
the version number on ``develop``.

.. _`pull request`:

Opening a Pull Request
======================

Depending on the type of change you are making, the branching model may
require merging your work into one or two target branches (typically one is
``develop``). Be sure to open a pull request for each target branch.

1. Open a pull request (PR) to merge your forked branch, the
   **candidate**, into **target** branch of this repository.
2. Add Raj (``prkumar``) as a reviewer.
3. If your PR fails the Travis CI check, investigate the build log for
   cause of failure, address locally, and update the candidate branch. Repeat
   this step until the PR passes the Travis CI check.
4. If your PR fails the Coveralls check, check the PR's Coveralls' report
   to identify modules experiencing a test coverage drop. Improve testing
   locally, then update the candidate branch.
5. Once all checks have passed and the assigned reviewers have approved,
   your changes will be **squashed and merged** into the target branch.

.. _tests:

Testing
=======

We use the unit testing framework ``pytest``. Kept under the `tests`
directory, unit tests are written in Python modules with the filename
pattern ``test_*.py``.

Notably, ``conftest.py`` defines several `pytest fixtures
<https://docs.pytest.org/en/latest/fixture.html>`_, for injecting an
instance of an interface (defined in ``uplink.interfaces``) or utility
(defined in ``uplink.helpers``) class into your tests.

Style Guide
===========

To maintain a consistent code style with the rest of Uplink, follow the `Google
Python Style Guide`_.

Notably, we use a Sphinx plugin that can parse docstrings adherent to this
style. Checkout `this page
<http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_
for examples of Google Python Style Guide docstrings.

.. _`Google Python Style Guide`: https://google.github.io/styleguide/pygu