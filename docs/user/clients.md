# Clients

To use a common English metaphor: Uplink stands on the shoulders of
giants.

Uplink doesn't implement any code to handle HTTP protocol stuff
directly; for that, the library delegates to an actual HTTP client, such
as Requests or Aiohttp. Whatever backing client you choose, when a
request method on a `uplink.Consumer` subclass is invoked, Uplink
ultimately interacts with the backing library's interface, at minimum to
submit requests and read responses.

This section covers the interaction between Uplink and the backing HTTP
client library of your choosing, including how to specify your
selection.

## Swapping Out the Default HTTP Session

By default, Uplink sends requests using the Requests library. You can
configure the backing HTTP client object using the `client` parameter of
the `uplink.Consumer` constructor:

``` python
github = GitHub(BASE_URL, client=...)
```

For example, you can use the `client` parameter to pass in your own
[Requests
session](http://docs.python-requests.org/en/master/user/advanced/#session-objects)
object:

``` python
session = requests.Session()
session.verify = False
github = GitHub(BASE_URL, client=session)
```

Further, this also applies for session objects from other HTTP client
libraries that Uplink supports, such as `aiohttp` (i.e., a custom
`aiohttp.ClientSession` works here, as well).

Following the above example, the `client` parameter also accepts an
instance of any `requests.Session` subclass. This makes it easy to
leverage functionality from third-party Requests extensions, such as
[requests-oauthlib](https://github.com/requests/requests-oauthlib), with
minimal integration overhead:

``` python
from requests_oauthlib import OAuth2Session

session = OAuth2Session(...)
api = MyApi(BASE_URL, client=session)
```

## Synchronous vs. Asynchronous

Notably, Requests blocks while waiting for a response from the server.
For non-blocking requests, Uplink comes with built-in (but optional)
support for `aiohttp` and `twisted`.

For instance, you can provide the `uplink.AiohttpClient` when
constructing a `uplink.Consumer` instance:

``` python
from uplink import AiohttpClient

github = GitHub(BASE_URL, client=AiohttpClient())
```

Checkout [this example on
GitHub](https://github.com/prkumar/uplink/tree/master/examples/async-requests)
for more.

## Handling Exceptions From the Underlying HTTP Client Library

Each `uplink.Consumer` instance has an `exceptions
<uplink.Consumer.exceptions>` property that exposes an enum of standard
HTTP client exceptions that can be handled:

``` python
try:
    repo = github.create_repo(name="myproject", auto_init=True)
except github.exceptions.ConnectionError:
    # Handle client socket error:
    ...
```

This approach to handling exceptions decouples your code from the
backing HTTP client, improving code reuse and testability.

Here are the HTTP client exceptions that are exposed through this property:

:   -   `BaseClientException`: Base exception for client connection
        errors.
    -   `ConnectionError`: A client socket error occurred.
    -   `ConnectionTimeout`: The request timed out while trying to
        connect to the remote server.
    -   `ServerTimeout`: The server did not send any data in the
        allotted amount of time.
    -   `SSLError`: An SSL error occurred.
    -   `InvalidURL`: URL used for fetching is malformed.

Of course, you can also explicitly catch a particular client error from
the backing client (e.g., `requests.FileModeWarning`). This may be
useful for handling exceptions that are not exposed through the
`Consumer.exceptions <uplink.Consumer.exceptions>` property, for
example:

``` python
try:
    repo = github.create_repo(name="myproject", auto_init=True)
except aiohttp.ContentTypeError:
    ...
```

### Handling Client Exceptions within an `@error_handler`

The `@error_handler <uplink.error_handler>` decorator registers a
callback to deal with exceptions thrown by the backing HTTP client.

To provide the decorated callback a reference to the `Consumer` instance
at runtime, set the decorator's optional argument `requires_consumer` to
`True`. This enables the error handler to leverage the consumer's
`exceptions
<uplink.Consumer.exceptions>` property:

``` python
@error_handler(requires_consumer=True)
def raise_api_error(consumer, exc_type, exc_val, exc_tb):
    """Wraps client error with custom API error"""
    if isinstance(exc_val, consumer.exceptions.ServerTimeout):
        # Handle the server timeout specifically:
        ...

class GitHub(Consumer):
    @raise_api_error
    @post("user/repo")
    def create_repo(self, name: Field):
        """Create a new repository."""
```
