# Standard library imports
import os
from setuptools import setup, find_packages

# Read package metadata from __about__.py, to avoid importing the whole
# package prior to installation.
about = dict()
with open(os.path.join("uplink", "__about__.py")) as fp:
    exec(fp.read(), about)

metadata = dict({
    "name": "uplink",
    "author": "P. Raj Kumar",
    "author_email": "raj.pritvi.kumar@gmail.com",
    "description": "A modular framework for building API clients.",
    "classifiers": [
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
    "keywords": "http api rest clients retrofit",
    "packages": find_packages(exclude=("tests",)),
    "install_requires": [
        "requests>=2.18.0"
        "uritemplate>=3.0.0"
    ],
}, **about)

if __name__ == "__main__":
    setup(**metadata)
