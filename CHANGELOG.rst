Changelog
*********

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_, and this project adheres to the
`Semantic Versioning`_ scheme.

0.2.0_ - 2017-11-03
===================
Added
-----
- The class ``uplink.Consumer``. Consumer classes should inherit this base
  class, and creating consumer instances happens through instantiation.
- Support for ``asyncio`` for Python 3.4 and above.
- Support for ``twisted`` for all supported Python versions.

Changed
-------
- **BREAKING**: Invoking a consumer method now builds and executes the request,
  removing the extra step of calling the ``execute`` method.

Deprecated
----------
- Building consumer instances with ``uplink.build``. Instead, Consumer classes
  should inherit ``uplink.Consumer``.

Fixed
-----
- Header link for version 0.1.1 in changelog.

0.1.1_ - 2017-10-21
===================
Added
-----
- Contribution guide, ``CONTRIBUTING.rst``.
- "Contributing" Section in README.rst that links to contribution guide.
- ``AUTHORS.rst`` file for listing project contributors.
- Adopt `Contributor Covenant Code of Conduct`_.

.. _`Contributor Covenant Code of Conduct`: https://www.contributor-covenant.org/version/1/4/code-of-conduct.html

Changed
-------
- Replaced tentative contributing instructions in preview notice on
  documentation homepage with link to contribution guide.

0.1.0 - 2017-10-19
==================
Added
-----
- Python ports for almost all method and argument annotations in Retrofit_.
- Adherence to the variation of the semantic versioning scheme outlined in
  the official Python package distribution tutorial.
- MIT License
- Documentation with introduction, instructions for installing, and quick
  getting started guide covering the builder and all method and argument
  annotations.
- README that contains GitHub API v3 example, installation instructions with
  ``pip``, and link to online documentation.

.. _Retrofit: http://square.github.io/retrofit/
.. _`Keep a Changelog`: http://keepachangelog.com/en/1.0.0/
.. _`Semantic Versioning`: https://packaging.python.org/tutorials/distributing-packages/#semantic-versioning-preferred

.. _0.2.0: https://github.com/prkumar/uplink/compare/v0.1.1...v0.2.0
.. _0.1.1: https://github.com/prkumar/uplink/compare/v0.1.0...v0.1.1