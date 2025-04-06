# Converters

The `converter` parameter of the `uplink.Consumer` constructor accepts a custom adapter class that handles serialization of HTTP request properties and deserialization of HTTP response objects:

```python
github = GitHub(BASE_URL, converter=...)
```

Starting with version v0.5, some out-of-the-box converters are included automatically and don't need to be explicitly provided through the `converter` parameter. These implementations are detailed below.

## Marshmallow

Uplink comes with optional support for `marshmallow`.

::: uplink.converters.MarshmallowConverter
    options:
      members: false
      inherited_members: false

!!! note
    Starting with version v0.5, this converter factory is automatically included if you have `marshmallow` installed, so you don't need to provide it when constructing your consumer instances.

## Pydantic

!!! info "New in version v0.9.2"
    Uplink comes with optional support for `pydantic`.

::: uplink.converters.PydanticConverter
    options:
      members: false
      inherited_members: false

!!! note
    Starting with version v0.9.2, this converter factory is automatically included if you have `pydantic` installed, so you don't need to provide it when constructing your consumer instances.

## Converting Collections

!!! info "New in version v0.5.0"
    Uplink can convert collections of a type, such as deserializing a response body into a list of users. If you have `typing` installed (the module is part of the standard library starting Python 3.5), you can use type hints (see [PEP 484](https://www.python.org/dev/peps/pep-0484/)) to specify such conversions. You can also leverage this feature without `typing` by using one of the proxy types defined in `uplink.types`.

The following converter factory implements this feature and is automatically included, so you don't need to provide it when constructing your consumer instance:

::: uplink.converters.TypingConverter
    options:
      members: false
      inherited_members: false

Here are the collection types defined in `uplink.types`. You can use these or the corresponding type hints from `typing` to leverage this feature:

::: uplink.types.List
    options:
      show_bases: false
      members: false
      inherited_members: false

::: uplink.types.Dict
    options:
      show_bases: false
      members: false
      inherited_members: false

## Writing Custom JSON Converters

As a shorthand, you can define custom JSON converters using the `@loads.from_json` (deserialization) and `@dumps.to_json` (serialization) decorators.

These classes can be used as decorators to create converters of a class and its subclasses:

```python
# Creates a converter that can deserialize the given `json` in to an
# instance of a `Model` subtype.
@loads.from_json(Model)
def load_model_from_json(model_type, json):
    ...
```

!!! note
    Unlike consumer methods, these functions should be defined outside of a class scope.

To use the converter, provide the generated converter object when instantiating a `uplink.Consumer` subclass, through the `converter` constructor parameter:

```python
github = GitHub(BASE_URL, converter=load_model_from_json)
```

Alternatively, you can add the `@install` decorator to register the converter function as a default converter, meaning the converter will be included automatically with any consumer instance and doesn't need to be explicitly provided through the `converter` parameter:

```python
from uplink import install, loads

# Register the function as a default loader for the given model class.
@install
@loads.from_json(Model)
def load_model_from_json(model_type, json):
    ...
```

::: uplink.loads
    options:
      members: ["from_json"]

::: uplink.dumps
    options:
      ffmembers: ["to_json"]
