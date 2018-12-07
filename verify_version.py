# Standard library imports
import argparse
import os
import re

RELEASE_BRANCH = "stable"


def is_release(version):
    return re.match(r'^([1-9]\d*!)?(0|[1-9]\d*)(\.(0|[1-9]\d*))*$', version) is not None


def is_canonical(version):
    return re.match(r'^([1-9]\d*!)?(0|[1-9]\d*)(\.(0|[1-9]\d*))*((a|b|rc)(0|[1-9]\d*))?(\.post(0|[1-9]\d*))?(\.dev(0|[1-9]\d*))?$', version) is not None


def _get_current_version():
    about = dict()
    with open(os.path.join("uplink", "__about__.py")) as fp:
        exec(fp.read(), about)
    return about.get("__version__", None)


def verify_version(branch, tag):
    # Get version defined in package or from the tag
    version = _get_current_version()
    assert branch is not None, "The branch is not defined."
    assert version is not None, "The version is not defined in uplink/__about__.py."

    # Avoid official releases on development branches
    if branch != RELEASE_BRANCH:
        assert not is_release(version), "Cannot deploy official release [%s] from development branch" % version

    # Make sure the tag version and version in __about__.py are the same
    if tag:
        assert tag == ("v" + version), "The tag [%s] does not match the current version in uplink/__about__.py [%s]" % (tag, version)

    assert is_canonical(version), "The version string [%s] violates PEP-440"
    return version


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", required=True)
    parser.add_argument("--tag", nargs="?")
    args = parser.parse_args()

    print(verify_version(args.branch, args.tag))


if __name__ == "__main__":
    main()
