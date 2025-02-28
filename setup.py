# Standard library imports
import os

from setuptools import find_packages, setup


def read(filename):
    with open(filename) as stream:
        return stream.read()


# Read package metadata from __about__.py, to avoid importing the whole
# package prior to installation.
about = {}
with open(os.path.join("uplink", "__about__.py")) as fp:
    exec(fp.read(), about)
    about = {k.strip("_"): about[k] for k in about}

install_requires = [
    "requests>=2.18.0",
    "six>=1.13.0",
    "uritemplate>=3.0.0",
    "setuptools",
]

extras_require = {
    "marshmallow": ["marshmallow>=2.15.0"],
    "pydantic": ["pydantic>=2.0.0"],
    "aiohttp": "aiohttp>=2.3.0",
    "twisted": "twisted>=17.1.0",
    "typing": ["typing>=3.6.4"],
    "tests": [
        "pytest",
        "pytest-mock",
        "pytest-cov",
        "pytest-twisted",
        "pytest-asyncio",
    ],
}

metadata = {
    "author": "P. Raj Kumar",
    "author_email": "raj.pritvi.kumar@gmail.com",
    "url": "https://uplink.readthedocs.io/",
    "project_urls": {
        "Source": "https://github.com/prkumar/uplink",
    },
    "license": "MIT",
    "description": "A Declarative HTTP Client for Python.",
    "long_description": read("README.rst"),
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    "keywords": "http api rest client retrofit",
    "packages": find_packages(exclude=("tests", "tests.*")),
    "install_requires": install_requires,
    "extras_require": extras_require,
    "python_requires": ">=3.10.0",
}
metadata = dict(metadata, **about)

if __name__ == "__main__":
    setup(name="uplink", **metadata)
