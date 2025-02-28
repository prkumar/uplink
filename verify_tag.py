# Standard library imports
import argparse
import os
import re


def is_appropriate_tag(version, tag):
    # Make sure the tag version and version in __about__.py match
    return (
        re.match(
            r"^" + tag + r"(\.post(0|[1-9]\d*))?(\.dev(0|[1-9]\d*))?$", "v" + version
        )
        is not None
    )


def is_canonical(version):
    return (
        re.match(
            r"^([1-9]\d*!)?(0|[1-9]\d*)(\.(0|[1-9]\d*))*((a|b|rc)(0|[1-9]\d*))?(\.post(0|[1-9]\d*))?(\.dev(0|[1-9]\d*))?$",
            version,
        )
        is not None
    )


def _get_current_version():
    about = {}
    with open(os.path.join("uplink", "__about__.py")) as fp:
        exec(fp.read(), about)
    return about.get("__version__", None)


def verify_version(tag):
    # Get version defined in package
    version = _get_current_version()
    assert version is not None, "The version is not defined in uplink/__about__.py."
    assert tag is not None, "The tag is not defined."
    assert is_canonical(version), "The version string [%s] violates PEP-440"
    assert is_appropriate_tag(version, tag), (
        f"The tag [{tag}] does not match the current version in uplink/__about__.py [{version}]"
    )
    return version


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()
    return verify_version(args.tag)


if __name__ == "__main__":
    print(main())
