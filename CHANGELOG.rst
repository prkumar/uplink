Changelog
*********

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_, and this project adheres to the
`Semantic Versioning`_ scheme.

0.5.2_ - 2018-5-30
==================
Fixed
-----
- Applying ``returns.json`` decorator without arguments should produce JSON
  responses when the decorated method is lacking a return value annotation.

0.5.1_ - 2018-4-10
==================
Added
-----
- Decorator ``uplink.returns.model`` for specifying custom return type without
  indicating a specific data deserialization format.

Fixed
-----
- Have ``uplink.Body`` decorator accept any type, not just mappings.
- Reintroduce the ``uplink.returns`` decorator.

0.5.0_ - 2018-4-06
==================
Added
-----
- Decorators for convenient registration of custom serialization.
  (``uplink.dumps``) and deserialization (``uplink.loads``) strategies.
- Support for setting nested JSON fields with ``uplink.Field`` and
  ``uplink.json``.
- Optional ``args`` parameter to HTTP method decorators (e.g., ``uplink.get``)
  for another Python 2.7-compatible alternative to annotating consumer method
  arguments with function annotations.
- Decorator ``uplink.returns.json`` for converting HTTP response bodies into
  JSON objects or custom Python objects.
- Support for converting collections (e.g., converting a response body into a
  list of users).

Changed
-------
- Leveraging built-in converters (such as ``uplink.converters.MarshmallowConverter``)
  no longer requires providing the converter when instantiating an
  ``uplink.Consumer`` subclass, as these converters are now implicitly included.

Fixed
-----
- ``uplink.response_handler`` and ``uplink.error_handler`` properly
  adopts the name and docstring of the wrapped function.

0.4.1_ - 2018-3-10
==================
Fixed
-----
- Enforce method-level decorators override class-level decorators when they conflict.

0.4.0_ - 2018-2-10
==================
Added
-----
- Support for Basic Authentication.
- The ``response_handler`` decorator for defining custom response handlers.
- The ``error_handler`` decorator for defining custom error handlers.
- The ``inject`` decorator for injecting other kinds of middleware.
- The ``Consumer._inject`` method for adding middleware to a consumer
  instance.
- Support for annotating constructor arguments of a ``Consumer`` subclass
  with built-in function annotations like ``Query`` and ``Header``.

0.3.0_ - 2018-1-09
==================
Added
-----
- HTTP HEAD request decorator by `@brandonio21`_.
- Support for returning deserialized response objects using ``marshmallow``
  schemas.
- Constructor parameter for ``Query`` and ``QueryMap`` to
  support already encoded URL parameters.
- Support for using ``requests.Session`` and ``aiohttp.ClientSession``
  instances with the ``client`` parameter of the ``Consumer``
  constructor.

Changed
-------
- ``aiohttp`` and ``twisted`` are now optional dependencies/extras.

Fixed
-----
- Fix for calling a request method with ``super``, by `@brandonio21`_.
- Fix issue where method decorators would incorrectly decorate inherited
  request methods.

0.2.2_ - 2017-11-23
===================
Fixed
-----
- Fix for error raised when an object that is not a class is passed into the
  ``client`` parameter of the ``Consumer`` constructor, by `@kadrach`_.

0.2.0_ - 2017-11-03
===================
Added
-----
- The class ``uplink.Consumer`` by `@itstehkman`_. Consumer classes should
  inherit this base.
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

.. General Links
.. _Retrofit: http://square.github.io/retrofit/
.. _`Keep a Changelog`: http://keepachangelog.com/en/1.0.0/
.. _`Semantic Versioning`: https://packaging.python.org/tutorials/distributing-packages/#semantic-versioning-preferred

.. Releases
.. _0.5.2: https://github.com/prkumar/uplink/compare/v0.5.1...v0.5.2
.. _0.5.1: https://github.com/prkumar/uplink/compare/v0.5.0...v0.5.1
.. _0.5.0: https://github.com/prkumar/uplink/compare/v0.4.1...v0.5.0
.. _0.4.1: https://github.com/prkumar/uplink/compare/v0.4.0...v0.4.1
.. _0.4.0: https://github.com/prkumar/uplink/compare/v0.3.0...v0.4.0
.. _0.3.0: https://github.com/prkumar/uplink/compare/v0.2.2...v0.3.0
.. _0.2.2: https://github.com/prkumar/uplink/compare/v0.2.0...v0.2.2
.. _0.2.0: https://github.com/prkumar/uplink/compare/v0.1.1...v0.2.0
.. _0.1.1: https://github.com/prkumar/uplink/compare/v0.1.0...v0.1.1

.. Contributors
.. _@brandonio21: https://github.com/brandonio21
.. _@itstehkman: https://github.com/itstehkman
.. _@kadrach: https://github.com/kadrach
