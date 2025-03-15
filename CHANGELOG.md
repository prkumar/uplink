# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to the
[Semantic Versioning] scheme.

## [0.9.7] - 2022-03-10

### Fixed

- Fix behavior of async `@response_handler` with `AiohttpClient`. ([#256])

## [0.9.6] - 2022-01-24

### Added

- Add a new base class, `uplink.retry.RetryBackoff`, which can be extended to
  implement custom backoff strategies. An instance of a `RetryBackoff` subclass
  can be provided through the `backoff` argument of the `@retry` decorator.
  ([#238])

### Changed

- Bump minimum version of `six` to `1.13.0`. ([#246])

### Fixed

- Fix `@returns.json` to cast JSON response (or field referenced by the `key`
  argument) using the `type` argument when the given type is callable. This
  restores behavior that was inadvertently changed in v0.9.3. ([#215])
- Remove all usages of `asyncio.coroutine` in the library code to fix warnings
  related to the function's deprecation in Python 3.8+. ([#203])

## [0.9.5] - 2022-01-04

### Added

- Add Python 3.8, 3.9, and 3.10 as officially supported. ([#237])

### Fixed

- Fix `FieldMap` and `PartMap` from raising `NoneType` error. ([#221])
- Fix Python 2.7 support. ([#217])

### Deprecated

- Python 2.7 support will be removed in v0.10.0.

## [0.9.4] - 2021-02-15

### Fixed

- A type set as a consumer method's return annotation should not be used to
  deserialize a response object if no registered converters can handle the type.
  ([3653a672ee])

## [0.9.3] - 2020-11-22

### Added

- Support for serialization using a subclass of [pydantic]'s `BaseModel` that
  contains fields of a complex type, such as `datetime`.
  ([#207] by [@leiserfg])
- Support for passing a subclass of [pydantic]'s `BaseModel` as the request
  body. ([#209] by [@lust4life])

## [0.9.2] - 2020-10-18

### Added

- Support for (de)serializing subclasses of [pydantic]'s `BaseModel`
  ([#200] by [@gmcrocetti])

### Fixed

- Using the `@get`, `@post`, `@patch`, etc. decorators should retain the
  docstring of the wrapped method ([#198])
- The `Body` and `Part` argument annotations should support uploading binary
  data ([#180], [#183], [#204])

## [0.9.1] - 2020-02-08

### Fixed

- Omit `Header` argument from request when its value is `None`.
  ([#167], [#169])
- Fix `AttributeError` raised on usage of `uplink.Url`.
  ([#164], [#165] by [@cognifloyd])

### Changed

- Exclude `tests` subpackages from wheel.
  ([#188] by [@daa])

## [0.9.0] - 2019-06-05

### Added

- Create consumer method templates to reduce boilerplate in request
  definitions. ([#151], [#159])
- `Context` argument annotation to pass request-specific information to
  middleware. ([#143], [#155])
- `Session.context` property to pass session-specific information to
  middleware. ([#143], [#155])
- Built-in authentication support for API tokens in the querystring
  and header, Bearer tokens, and multi-auth. ([#137])

### Fixed

- Schema defined using `@returns.*` decorators should override the
  consumer method's return annotation. ([#144], [#154])
- `@returns.*` decorators should propagate to all consumer method when used
  as a class decorator. ([#145], [#154])
- Decorating a `Consumer` subclass no longer affects other subclasses. ([#152])

### Changed

- Rename `uplink.retry.stop.DISABLE` to `uplink.retry.stop.NEVER`

## [0.8.0] - 2019-02-16

### Added

- A `retry` decorator to enable reattempts of failed requests. ([#132])
- A `ratelimit` decorator to constrain consumers to making some maximum number
  of calls within a given time period. ([#132])
- `Timeout` argument annotation to be able to pass the timeout as a consumer
  method argument or to inject it as a transaction hook using a `Consumer`
  instance's `_inject` method. ([#133] by [@daa])

### Changed

- `Consumer` subclasses now inherit class decorators from their
  `Consumer` parents, so those decorators are also applied to the subclasses'
  methods that are decorated with `@get`, `@post`, `@patch`, etc.
  ([#138] by [@daa])

### Fixed

- Memory leaks in `RequestsClient` and `AiohttpClient` caused by
  use of `atexit.register`, which was holding references to session objects
  and preventing the garbage collector from freeing memory reserved for those
  objects. ([#134] by [@SakornW])

## [0.7.0] - 2018-12-06

### Added

- `Consumer.exceptions` property for handling common client exceptions in a
  client-agnostic way. ([#117])
- Optional argument `requires_consumer` for `response_handler` and
  `error_handler`; when set to `True`, the registered callback should accept
  a reference to a `Consumer` instance as its leading argument.
  ([#118])

### Changed

- For a `Query`-annotated argument, a `None` value indicates that the query
  parameter should be excluded from the request. Previous behavior was to encode
  the parameter as `...?name=None`. To retain this behavior, specify the
  new `encode_none` parameter (i.e., `Query(..., encode_none="None")`).
  ([#126] by [@nphilipp])

### Fixed

- Support for changes to `Schema().load` and `Schema().dump` in
  `marshmallow` v3.
  ([#109])

## [0.6.1] - 2018-9-14

### Changed

- When the `type` parameter of a function argument annotation, such as
  `Query` or `Body`, is omitted, the type of the annotated argument's
  value is no longer used to determine how to convert the value before it's
  passed to the backing client; the argument's value is converted only when
  its `type` is explicitly set.

## [0.6.0] - 2018-9-11

### Added

- The `session` property to the `Consumer` base class, exposing the
  consumer instance's configuration and allowing for the persistence of
  certain properties across requests sent from that instance.
- The `params` decorator, which when applied to a method of a `Consumer`
  subclass, can add static query parameters to each API call.
- The `converters.Factory` base class for defining integrations with
  other serialization formats and libraries.
- The `uplink.install` decorator for registering extensions, such as a
  custom `converters.Factory` implementation, to be applied broadly.

### Fixed

- Issue with detecting `typing.List` and `typing.Dict` for converting
  collections on Python 3.7.
- `RuntimeWarning` that "`ClientSession.close` was never awaited" when
  using `aiohttp >= 3.0`.

### Changed

- When using the `marshmallow` integration, Uplink no longer suppresses
  `Schema` validation errors on deserialization; users can now handle these
  exceptions directly.

## [0.5.5] - 2018-8-01

### Fixed

- Issue with sending JSON list `Body` using `@json` annotation.

## [0.5.4] - 2018-6-26

### Fixed

- When using `uplink.AiohttpClient` with `aiohttp>=3.0`, the underlying
  `aiohttp.ClientSession` would remain open on program exit.

## [0.5.3] - 2018-5-31

### Fixed

- Issue where adding two or more response handlers (i.e., functions decorated
  with `uplink.response_handler`) to a method caused a `TypeError`.

## [0.5.2] - 2018-5-30

### Fixed

- Applying `returns.json` decorator without arguments should produce JSON
  responses when the decorated method is lacking a return value annotation.

## [0.5.1] - 2018-4-10

### Added

- Decorator `uplink.returns.model` for specifying custom return type without
  indicating a specific data deserialization format.

### Fixed

- Have `uplink.Body` decorator accept any type, not just mappings.
- Reintroduce the `uplink.returns` decorator.

## [0.5.0] - 2018-4-06

### Added

- Decorators for convenient registration of custom serialization
  (`uplink.dumps`) and deserialization (`uplink.loads`) strategies.
- Support for setting nested JSON fields with `uplink.Field` and
  `uplink.json`.
- Optional `args` parameter to HTTP method decorators (e.g., `uplink.get`)
  for another Python 2.7-compatible alternative to annotating consumer method
  arguments with function annotations.
- Decorator `uplink.returns.json` for converting HTTP response bodies into
  JSON objects or custom Python objects.
- Support for converting collections (e.g., converting a response body into a
  list of users).

### Changed

- Leveraging built-in converters (such as `uplink.converters.MarshmallowConverter`)
  no longer requires providing the converter when instantiating an
  `uplink.Consumer` subclass, as these converters are now implicitly included.

### Fixed

- `uplink.response_handler` and `uplink.error_handler` properly
  adopts the name and docstring of the wrapped function.

## [0.4.1] - 2018-3-10

### Fixed

- Enforce method-level decorators override class-level decorators when they conflict.

## [0.4.0] - 2018-2-10

### Added

- Support for Basic Authentication.
- The `response_handler` decorator for defining custom response handlers.
- The `error_handler` decorator for defining custom error handlers.
- The `inject` decorator for injecting other kinds of middleware.
- The `Consumer._inject` method for adding middleware to a consumer
  instance.
- Support for annotating constructor arguments of a `Consumer` subclass
  with built-in function annotations like `Query` and `Header`.

## [0.3.0] - 2018-1-09

### Added

- HTTP HEAD request decorator by [@brandonio21].
- Support for returning deserialized response objects using `marshmallow`
  schemas.
- Constructor parameter for `Query` and `QueryMap` to
  support already encoded URL parameters.
- Support for using `requests.Session` and `aiohttp.ClientSession`
  instances with the `client` parameter of the `Consumer`
  constructor.

### Changed

- `aiohttp` and `twisted` are now optional dependencies/extras.

### Fixed

- Fix for calling a request method with `super`, by [@brandonio21].
- Fix issue where method decorators would incorrectly decorate inherited
  request methods.

## [0.2.2] - 2017-11-23

### Fixed

- Fix for error raised when an object that is not a class is passed into the
  `client` parameter of the `Consumer` constructor, by [@kadrach].

## [0.2.0] - 2017-11-03

### Added

- The class `uplink.Consumer` by [@itstehkman]. Consumer classes should
  inherit this base class, and creating consumer instances happens through instantiation.
- Support for `asyncio` for Python 3.4 and above.
- Support for `twisted` for all supported Python versions.

### Changed

- **BREAKING**: Invoking a consumer method now builds and executes the request,
  removing the extra step of calling the `execute` method.

### Deprecated

- Building consumer instances with `uplink.build`. Instead, Consumer classes
  should inherit `uplink.Consumer`.

### Fixed

- Header link for version 0.1.1 in changelog.

## [0.1.1] - 2017-10-21

### Added

- Contribution guide, `CONTRIBUTING.rst`.
- "Contributing" Section in README.md that links to contribution guide.
- `AUTHORS.rst` file for listing project contributors.
- Adopt [Contributor Covenant Code of Conduct].

### Changed

- Replaced tentative contributing instructions in preview notice on
  documentation homepage with link to contribution guide.

## 0.1.0 - 2017-10-19

### Added

- Python ports for almost all method and argument annotations in [Retrofit].
- Adherence to the variation of the semantic versioning scheme outlined in
  the official Python package distribution tutorial.
- MIT License
- Documentation with introduction, instructions for installing, and quick
  getting started guide covering the builder and all method and argument
  annotations.
- README that contains GitHub API v3 example, installation instructions with
  `pip`, and link to online documentation.

[Keep a Changelog]: http://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: https://packaging.python.org/tutorials/distributing-packages/#semantic-versioning-preferred
[pydantic]: https://pydantic-docs.helpmanual.io/
[Retrofit]: http://square.github.io/retrofit/
[Contributor Covenant Code of Conduct]: https://www.contributor-covenant.org/version/1/4/code-of-conduct.html

[0.9.7]: https://github.com/prkumar/uplink/compare/v0.9.6...v0.9.7
[0.9.6]: https://github.com/prkumar/uplink/compare/v0.9.5...v0.9.6
[0.9.5]: https://github.com/prkumar/uplink/compare/v0.9.4...v0.9.5
[0.9.4]: https://github.com/prkumar/uplink/compare/v0.9.3...v0.9.4
[0.9.3]: https://github.com/prkumar/uplink/compare/v0.9.2...v0.9.3
[0.9.2]: https://github.com/prkumar/uplink/compare/v0.9.1...v0.9.2
[0.9.1]: https://github.com/prkumar/uplink/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/prkumar/uplink/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/prkumar/uplink/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/prkumar/uplink/compare/v0.6.1...v0.7.0
[0.6.1]: https://github.com/prkumar/uplink/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/prkumar/uplink/compare/v0.5.5...v0.6.0
[0.5.5]: https://github.com/prkumar/uplink/compare/v0.5.4...v0.5.5
[0.5.4]: https://github.com/prkumar/uplink/compare/v0.5.3...v0.5.4
[0.5.3]: https://github.com/prkumar/uplink/compare/v0.5.2...v0.5.3
[0.5.2]: https://github.com/prkumar/uplink/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/prkumar/uplink/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/prkumar/uplink/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/prkumar/uplink/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/prkumar/uplink/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/prkumar/uplink/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/prkumar/uplink/compare/v0.2.0...v0.2.2
[0.2.0]: https://github.com/prkumar/uplink/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/prkumar/uplink/compare/v0.1.0...v0.1.1

[#256]: https://github.com/prkumar/uplink/issues/256
[#246]: https://github.com/prkumar/uplink/issues/246
[#238]: https://github.com/prkumar/uplink/issues/238
[#237]: https://github.com/prkumar/uplink/discussions/237
[#221]: https://github.com/prkumar/uplink/issues/221
[#217]: https://github.com/prkumar/uplink/issues/217
[#215]: https://github.com/prkumar/uplink/issues/215
[#209]: https://github.com/prkumar/uplink/pull/209
[#207]: https://github.com/prkumar/uplink/pull/207
[#204]: https://github.com/prkumar/uplink/pull/204
[#203]: https://github.com/prkumar/uplink/issues/203
[#200]: https://github.com/prkumar/uplink/pull/200
[#198]: https://github.com/prkumar/uplink/pull/198
[#188]: https://github.com/prkumar/uplink/pull/188
[#183]: https://github.com/prkumar/uplink/pull/183
[#180]: https://github.com/prkumar/uplink/pull/180
[#169]: https://github.com/prkumar/uplink/pull/169
[#167]: https://github.com/prkumar/uplink/issues/167
[#165]: https://github.com/prkumar/uplink/pull/165
[#164]: https://github.com/prkumar/uplink/issues/164
[#159]: https://github.com/prkumar/uplink/pull/159
[#155]: https://github.com/prkumar/uplink/pull/155
[#154]: https://github.com/prkumar/uplink/pull/154
[#152]: https://github.com/prkumar/uplink/pull/152
[#151]: https://github.com/prkumar/uplink/issues/151
[#145]: https://github.com/prkumar/uplink/issues/145
[#144]: https://github.com/prkumar/uplink/issues/144
[#143]: https://github.com/prkumar/uplink/issues/143
[#138]: https://github.com/prkumar/uplink/pull/138
[#137]: https://github.com/prkumar/uplink/pull/137
[#134]: https://github.com/prkumar/uplink/pull/134
[#133]: https://github.com/prkumar/uplink/pull/133
[#132]: https://github.com/prkumar/uplink/pull/132
[#126]: https://github.com/prkumar/uplink/pull/126
[#118]: https://github.com/prkumar/uplink/pull/118
[#117]: https://github.com/prkumar/uplink/pull/117
[#109]: https://github.com/prkumar/uplink/pull/109

[3653a672ee]: https://github.com/prkumar/uplink/commit/3653a672ee0703119720d0077bb450649af5459c

[@daa]: https://github.com/daa
[@SakornW]: https://github.com/SakornW
[@brandonio21]: https://github.com/brandonio21
[@itstehkman]: https://github.com/itstehkman
[@kadrach]: https://github.com/kadrach
[@cognifloyd]: https://github.com/cognifloyd
[@gmcrocetti]: https://github.com/gmcrocetti
[@leiserfg]: https://github.com/leiserfg
[@lust4life]: https://github.com/lust4life
[@nphilipp]: https://github.com/nphilipp
