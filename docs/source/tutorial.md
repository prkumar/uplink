# Uplink

## Introduction

Uplink turns your HTTP API into a Python class.
```python
class GitHub(Consumer): 
    
    @get("users/{user}/repos")
    def list_repos(self, user):
        """List public repositories for the specified user."""
```

To access a webservice, simply instantiate the class.
```python
github = GitHub(base_url="https://api.github.com/")
```

Then, call methods to execute HTTP requests to your favorite webservice.
```python
response = github.list_repos("octocat")
```

### Synchronous vs. Asynchronous

By default, Uplink uses the powerful [`Requests`](http://docs.python-requests.org/en/master/)
library. So, the returned `response` is simply a [`requests.Response`](http://docs.python-requests.org/en/master/api/#requests.Response).

```python
print(response.json()) # {u'disk_usage': 216141, u'private_gists': 0, ...
```

For **asynchronous requests**, Uplink includes support for asyncio (for Python 3
.4+),

```python
# A consumer that returns awaitable responses using ``aiohttp``.
github = GitHub("https://api.github.com/", client=uplink.AiohttpClient())
```

And Twisted (for all supported Python versions).
```python
# A consumer that returns Twisted's Deferred responses.
github = GitHub("https://api.github.com/", client=uplink.TwistedClient())
```

## API Declaration

Decorators on the consumer methods and function annotations on its parameters
indicate how a request will be handled.

### Request Method
Every method must have an HTTP decorator that provides the request method and 
relative URL. There are five built-in annotations: `get`, `post`, `put`, 
`patch` and `delete`. The relative URL of the resource is specified in the 
decorator. 
```python
@get("users/list")
```

You can also specify query parameters in the URL.
```python
@get("users/list?sort=desc")
```

### URL Manipulation

TODO: Figure out how to better present this

A request URL can be updated dynamically using replacement blocks and 
parameters on the method. A replacement block is an alphanumeric string 
surrounded by `{` and `}`. A corresponding method parameter can be named
after the string:
```python
@get("group/{id}/users")
def group_list(self, id): pass
```

Alternatively, the corresponding method paramter can be annotated with `Path`
using the same string:
```python
@get("group/{id}/users")
def group_list(self, group_id: Path("id")): pass
```

Query parameters can also be added.
```python
@get("group/{id}/users")
def group_list(self, group_id: Path("id"), sort: Query("sort")): pass
```

For complex query parameter combinations, a mapping can be used:
```python
@get("group/{id}/users")
def group_list(self, group_id: Path("id"), options: QueryMap): pass
```

### Request Body

An object can be specified for use as an HTTP request body with the `Body`
annotation:

```python
@post("users/new")
def create_user(self, user: Body): pass
```

TODO: Word this better:
The keywargs parameter, `**kwargs` works well with the `Body` annotation:

```python
@post("users/new")
def create_user(self, **user_info: Body): pass
```

### Form Encoded and Multipart

Methods can also be declared to send form-encoded and multipart data. 

Form-encoded data is sent when `form_url_encoded` decorates the method. Each
key-value pair is annotated with `Field`, containing the name and the object 
providing the value. 
```python
@form_url_encoded
@post("user/edit")
def update_user(self, first_name: Field, last_name: Field): pass
```

Multipart requests are used when `multipart` decorates the method. Parts
are declared using the `Part` annotation:
```python
@multipart
@put("user/photo")
def update_user(self, photo: Part, description: Part): pass
```

TODO: Mention that parts should be given as Requests expects them

### Header Manipulation

You can set static headers for a method using the `headers` decorator.
```python
@headers("Cache-Control: max-age=640000")
@get("widget/list")
def widget_list(): pass
```
```python
@headers({
    "Accept": "application/vnd.github.v3.full+json",
    "User-Agent": "Uplink-Sample-App"
})
@get("users/{username}")
def get_user(self, username): pass
```

Headers that need to added to every request can be specified by decorating
the consumer class. 

### Synchronous vs. Asynchronous

TODO: talk about support with 




