# Standard library imports
import argparse
import os
import re

STABLE_BRANCH = "stable"
RELEASE_BRANCHES = ["stable", "master"]


def is_appropriate_tag(version, tag):
    # Make sure the tag version and version in __about__.py are matches
    return re.match(r'^' + tag + r'(\.post(0|[1-9]\d*))?(\.dev(0|[1-9]\d*))?$', "v" + version) is not None


def is_release(version):
    return re.match(r'^([1-9]\d*!)?(0|[1-9]\d*)(\.(0|[1-9]\d*))*$', version) is not None


def is_canonical(version):
    return re.match(r'^([1-9]\d*!)?(0|[1-9]\d*)(\.(0|[1-9]\d*))*((a|b|rc)(0|[1-9]\d*))?(\.post(0|[1-9]\d*))?(\.dev(0|[1-9]\d*))?$', version) is not None


def _get_current_version():
    about = dict()
    with open(os.path.join("uplink", "__about__.py")) as fp:
        exec(fp.read(), about)
    return about.get("__version__", None)


def should_release(branch, tag):
    # Release for tagged commits on either master or stable
    return branch in RELEASE_BRANCHES and bool(tag)


def verify_version(branch, tag):
    # Get version defined in package or from the tag
    version = _get_current_version()
    assert branch is not None, "The branch is not defined."
    assert version is not None, "The version is not defined in uplink/__about__.py."

    # Avoid official releases on development branches
    if branch != STABLE_BRANCH:
        assert not is_release(version), "Cannot deploy official release [%s] from development branch" % version

    # Make sure the tag version and version in __about__.py are the same
    assert is_appropriate_tag(version, tag), "The tag [%s] does not match the current version in uplink/__about__.py [%s]" % (tag, version)

    assert is_canonical(version), "The version string [%s] violates PEP-440"
    return version


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", required=True)
    parser.add_argument("--tag", nargs="?")
    args = parser.parse_args()
    if should_release(args.branch, args.tag):
        verify_version(args.branch, args.tag)
        return "true"
    else:
        return "false"


if __name__ == "__main__":
    print(main())
