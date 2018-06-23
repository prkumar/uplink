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

install_requires = ["requests>=2.18.0", "uritemplate>=3.0.0"]

extras_require = {
    "marshmallow": ["marshmallow>=2.15.0"],
    "aiohttp:python_version <= '3.4'": [],
    "aiohttp:python_version >= '3.4'": "aiohttp>=2.3.0",
    "twisted:python_version != '3.3'": "twisted>=17.1.0",
    "twisted:python_version == '3.3'": "twisted<=17.9.0",
    "typing": ["typing>=3.6.4"],
    "tests": ["pytest", "pytest-mock", "pytest-cov"],
}

metadata = {
    "name": "uplink",
    "author": "P. Raj Kumar",
    "author_email": "raj.pritvi.kumar@gmail.com",
    "url": "https://uplink.readthedocs.io/",
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
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    "keywords": "http api rest client retrofit",
    "packages": find_packages(exclude=("tests",)),
    "install_requires": install_requires,
    "extras_require": extras_require,
}
metadata = dict(metadata, **about)

if __name__ == "__main__":
    setup(**metadata)
