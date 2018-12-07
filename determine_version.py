# Standard library imports
import argparse
import os
import re

DEVELOPMENT_BRANCH_NAME = "master"


def is_canonical(version):
    return re.match(r'^([1-9]\d*!)?(0|[1-9]\d*)(\.(0|[1-9]\d*))*((a|b|rc)(0|[1-9]\d*))?(\.post(0|[1-9]\d*))?(\.dev(0|[1-9]\d*))?$', version) is not None


def _get_current_version():
    about = dict()
    with open(os.path.join("uplink", "__about__.py")) as fp:
        exec(fp.read(), about)
    return about.get("__version__", None)


def _get_dev_version(build_number):
    return ".dev" + build_number


def build_version(tag, build_number=None):
    # Get version defined in package or from the tag
    version = _get_current_version()
    assert version is not None, "The version in uplink/__about__.py is undefined."

    if not tag:
        assert build_number is not None
        version += _get_dev_version(build_number)
    else:
        # Make sure the tag version and version in __about__.py are the same
        assert tag == version, "The tag [%s] does not match the current version in uplink/__about__.py [%s]" % (tag, version)

    assert is_canonical(version), "The version string [%s] violates PEP-440"
    return version


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", nargs="?")
    parser.add_argument("--build-number", required=True)
    args = parser.parse_args()

    print(build_version(args.tag, args.build_number))


if __name__ == "__main__":
    main()
