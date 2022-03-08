# Standard library imports
import os
from setuptools import setup, find_packages


def read(filename):
    with open(filename) as stream:
        return stream.read()


# Read package metadata from __about__.py, to avoid importing the whole
# package prior to installation.
about = dict()
with open(os.path.join("uplink", "__about__.py")) as fp:
    exec(fp.read(), about)
    about = dict((k.strip("_"), about[k]) for k in about)

install_requires = ["requests>=2.18.0", "six>=1.13.0", "uritemplate>=3.0.0"]

extras_require = {
    "marshmallow": ["marshmallow>=2.15.0"],
    "pydantic:python_version >= '3.6'": ["pydantic>=1.6.1"],
    "aiohttp:python_version <= '3.4'": [],
    "aiohttp:python_version >= '3.4'": "aiohttp>=2.3.0",
    "twisted:python_version != '3.3' and python_version != '3.4'": "twisted>=17.1.0",
    # Twisted 18.4.0 dropped py3.3 support
    "twisted:python_version == '3.3'": "twisted<=17.9.0",
    # Twisted 19.7.0 dropped py3.4 support
    "twisted:python_version == '3.4'": "twisted<=19.2.1",
    "typing": ["typing>=3.6.4"],
    "tests": ["pytest", "pytest-mock", "pytest-cov", "pytest-twisted"],
    "tests:python_version >= '3.5'": ["pytest-asyncio"],
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
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    "keywords": "http api rest client retrofit",
    "packages": find_packages(exclude=("tests", "tests.*")),
    "install_requires": install_requires,
    "extras_require": extras_require,
}
metadata = dict(metadata, **about)

if __name__ == "__main__":
    setup(name="uplink", **metadata)
