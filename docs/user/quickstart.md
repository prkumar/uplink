# Quickstart

Ready to write your first API client with Uplink? This guide will walk
you through what you'll need to know to get started.

**First**, make sure you've `installed (or updated) Uplink <install>`:

    pip install -U uplink

## Defining an API Client

Writing a **structured** API client with Uplink is very simple.

To start, create a subclass of `uplink.Consumer`. For example, here's
the beginning of our GitHub client (we'll add some methods to this class
soon):

``` python
from uplink import Consumer

class GitHub(Consumer):
   ...
```

When creating an instance of this consumer, we can use the `base_url`
constructor argument to identify the target service. In our case, it's
GitHub's public API:

``` python
github = GitHub(base_url="https://api.github.com/")
```

!!! note
`base_url` is especially useful for creating clients that target
separate services with similar APIs; for example, we could use this
GitHub consumer to also create clients for any GitHub Enterprise
instance for projects hosted outside of the public
[GitHub.com](https://github.com) service. Another example is creating
separate clients for a company's production and staging environments,
which are typically hosted on separate domains but expose the same API.

So far, this class looks like any other Python class. The real magic
happens when you define methods to interact with the webservice using
Uplink's HTTP method decorators, which we cover next.

## Making a Request

With Uplink, making a request to a webservice is as simple as invoking a
method.

Any method of a `Consumer` subclass can be decorated with one of
Uplink's HTTP method decorators: `@get <uplink.get>`,
`@post <uplink.post>`, `@put <uplink.put>`, `@patch <uplink.patch>`,
`@head <uplink.head>`, and `@delete <uplink.delete>`:

``` python
class GitHub(Consumer):
    @get("repositories")
    def get_repos(self):
        """List all public repositories."""
```

As shown above, the method's body can be left empty.

The decorator's first argument is the resource endpoint: i.e., the
relative path from `base_url`, which we covered above:

``` python
@get("repositories")
```

!!! note
To build a request's absolute URL, Uplink resolves the relative path
against the `Consumer`'s base url using `urljoin
<urllib.parse.urljoin>`, which implements the [RFC
3986](https://tools.ietf.org/html/rfc3986#section-5) standards. For a
simplified overview of these standards, see [these recommendations and
examples](https://square.github.io/retrofit/2.x/retrofit/retrofit2/Retrofit.Builder.html#baseUrl-okhttp3.HttpUrl-)
from Retrofit's documentation.

You can also specify query parameters:

``` python
@get("repositories?since=364")
```

Finally, invoke the method to send a request:

``` python
>>> github = GitHub(base_url="https://api.github.com/")
>>> github.get_repos()
<Response [200]>
>>> _.url
https://api.github.com/repositories
```

By default, uplink uses
[Requests](https://github.com/requests/requests), so the response we get
back from GitHub is wrapped inside a `requests.Response` instance. (If
you want, you can `swap out <swap_default_http_client>` Requests for a
different backing HTTP client, such as `aiohttp <sync_vs_async>`.)

## Path Parameters

Resource endpoints can include [URI template
parameters](https://tools.ietf.org/html/rfc6570) that depend on method
arguments. A simple URI parameter is an alphanumeric string surrounded
by `{` and `}`.

To match the parameter with a method argument, either match the
argument's name with the alphanumeric string, like so:

``` python
@get("users/{username}")
def get_user(self, username): pass
```

or use the `uplink.Path` annotation.

``` python
@get("users/{username}")
def get_user(self, name: Path("username")): pass
```

## Query Parameters

Query parameters can be added dynamically using the `uplink.Query`
argument annotation.

``` python
@get("users/{username}/repos")
def get_repos(self, username, sort: Query): pass
```

Setting a default value for the query parameter works like you'd expect
it to:

``` python
@get("users/{username}/repos")
def get_repos(self, username, sort: Query = "created"): pass
```

To make the query parameter optional, set the argument's default value
to `None`. Then, if the argument is not specified at runtime, the
parameter will not appear in the request.

``` python
@get("users/{username}/repos")
def get_repos(self, username, sort: Query = None): pass
```

Useful for "catch-all" or complex query parameter combinations, the
`uplink.QueryMap` annotation accepts a mapping of query parameters:

``` python
@get("users/{username}/repos")
def get_repos(self, username, **options: QueryMap): pass
```

You can set static query parameters for a method using the
`@params <uplink.params>` decorator.

``` python
@params({"client_id": "my-client", "client_secret": "****"})
@get("users/{username}")
def get_user(self, username): pass
```

`@params <uplink.params>` can be used as a class decorator for query
parameters that need to be included with every request:

``` python
@params({"client_id": "my-client", "client_secret": "****"})
class GitHub(Consumer):
    ...
```

## Request Headers

You can set static headers for a method using the
`@headers <uplink.headers>` decorator.

``` python
@headers({
    "Accept": "application/vnd.github.v3.full+json",
    "User-Agent": "Uplink-Sample-App"
})
@get("users/{username}")
def get_user(self, username): pass
```

`@headers <uplink.headers>` can be used as a class decorator for headers
that need to be added to every request:

``` python
@headers({
    "Accept": "application/vnd.github.v3.full+json",
    "User-Agent": "Uplink-Sample-App"
})
class GitHub(Consumer):
    ...
```

A request header can depend on the value of a method argument by using
the `uplink.Header` function parameter annotation:

``` python
@get("user")
def get_user(self, authorization: Header("Authorization"):
    """Get an authenticated user."""
```

## Request Body

The `uplink.Body` annotation identifies a method argument as the HTTP
request body:

``` python
@post("user/repos")
def create_repo(self, repo: Body): pass
```

This annotation works well with the **keyword arguments** parameter
(denoted by the `**` prefix):

``` python
@post("user/repos")
def create_repo(self, **repo_info: Body): pass
```

Moreover, this annotation is useful when using supported serialization
formats, such as `JSON <json>` and [Protocol
Buffers](https://github.com/prkumar/uplink-protobuf). Take a look at
`this guide <serialization>` for more about serialization with Uplink.

## Form Encoded, Multipart, and JSON Requests

Methods can also be declared to send form-encoded, multipart, and JSON
data.

Form-encoded data is sent when
`@form_url_encoded <uplink.form_url_encoded>` decorates the method. Each
key-value pair is annotated with a `uplink.Field` annotation:

``` python
@form_url_encoded
@patch("user")
def update_user(self, name: Field, email: Field): pass
```

Multipart requests are used when `@multipart <uplink.multipart>`
decorates the method. Parts are declared using the `uplink.Part`
annotation:

``` python
@multipart
@put("user/photo")
def upload_photo(self, photo: Part, description: Part): pass
```

JSON data is sent when `@json <uplink.json>` decorates the method. The
`uplink.Body` annotation declares the JSON payload:

``` python
@json
@patch("user")
def update_user(self, **user_info: uplink.Body):
    """Update an authenticated user."""
```

Alternatively, the `uplink.Field` annotation declares a JSON field:

``` python
@json
@patch("user")
def update_user_bio(self, bio: Field):
    """Update the authenticated user's profile bio."""
```

## Handling JSON Responses

Many modern public APIs serve JSON responses to their clients.

If your `uplink.Consumer` subclass accesses a JSON API, you can
decorate any method with `@returns.json <uplink.returns.json>` to
directly return the JSON response, instead of a response object, when
invoked:

``` python
class GitHub(Consumer):
    @returns.json
    @get("users/{username}")
    def get_user(self, username):
        """Get a single user."""
```

``` python
>>> github = GitHub("https://api.github.com")
>>> github.get_user("prkumar")
{'login': 'prkumar', 'id': 10181244, ...
```

You can also target a specific field of the JSON response by using the
decorator's `key` argument to select the target JSON field name:

``` python
class GitHub(Consumer):
    @returns.json(key="blog")
    @get("users/{username}")
    def get_blog_url(self, username):
        """Get the user's blog URL."""
```

``` python
>>> github.get_blog_url("prkumar")
"https://prkumar.io"
```

!!! note
JSON responses may represent existing Python classes in your application
(for example, a `GitHubUser`). Uplink supports this kind of conversion
(i.e., deserialization), and we detail this support in
`the next guide <serialization>`.

## Persistence Across Requests from a `Consumer`

The `session` property of a `uplink.Consumer` instance exposes the
instance's configuration and allows for the persistence of certain
properties across requests sent from that instance.

You can provide default headers and query parameters for requests sent
from a consumer instance through its `session` property, like so:

``` python
class GitHub(Consumer):

    def __init__(self, base_url, username, password):
        super(GitHub, self).__init__(base_url=base_url)

        # Creates the API token for this user
        api_key = create_api_key(username, password)

        # Send the API token as a query parameter with each request.
        self.session.params["access_token"] = api_key

    @get("user/repos")
    def get_user_repos(self, sort_by: Query("sort")):
        """Lists public repositories for the authenticated user."""
```

Headers and query parameters added through the `session` are applied to
all requests sent from the consumer instance.

``` python
github = GitHub("prkumar", "****")

# Both `access_token` and `sort` are sent with the request.
github.get_user_repos(sort_by="created")
```

Notably, in case of conflicts, the method-level headers and parameters
override the session-level, but the method-level properties are not
persisted across requests.

## Response and Error Handling

Sometimes, you need to validate a response before it is returned or even
calculate a new return value from the response. Or, you may need to
handle errors from the underlying client before they reach your users.

With Uplink, you can address these concerns by registering a callback
with one of these decorators:
`@response_handler <uplink.response_handler>` and
`@error_handler <uplink.error_handler>`.

`@response_handler <uplink.response_handler>` registers a callback to
intercept responses before they are returned (or deserialized):

``` python
def raise_for_status(response):
    """Checks whether or not the response was successful."""
    if 200 <= response.status_code < 300:
        # Pass through the response.
        return response

    raise UnsuccessfulRequest(response.url)

class GitHub(Consumer):
    @response_handler(raise_for_status)
    @post("user/repo")
    def create_repo(self, name: Field):
        """Create a new repository."""
```

`@error_handler <uplink.error_handler>` registers a callback to handle
an exception thrown by the underlying HTTP client (e.g.,
`requests.Timeout`):

``` python
def raise_api_error(exc_type, exc_val, exc_tb):
    """Wraps client error with custom API error"""
    raise MyApiError(exc_val)

class GitHub(Consumer):
    @error_handler(raise_api_error)
    @post("user/repo")
    def create_repo(self, name: Field):
        """Create a new repository."""
```

To apply a handler onto all methods of a `uplink.Consumer` subclass,
you can simply decorate the class itself:

``` python
@error_handler(raise_api_error)
class GitHub(Consumer):
    ...
```

Notably, the decorators can be stacked on top of one another to chain
their behaviors:

``` python
@response_handler(check_expected_headers)  # Second, check headers
@response_handler(raise_for_status)  # First, check success
class GitHub(Consumer):
    ...
```

Lastly, both decorators support the optional argument
`requires_consumer`. When this option is set to `True`, the registered
callback should accept a reference to the `Consumer` instance as its
leading argument:

``` python
@error_handler(requires_consumer=True)
def raise_api_error(consumer, exc_type, exc_val, exc_tb):
    """Wraps client error with custom API error"""
    ...

class GitHub(Consumer):
    @raise_api_error
    @post("user/repo")
    def create_repo(self, name: Field):
        """Create a new repository."""
```

## Retrying

[Networks are
unreliable](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing).
Requests can fail for various reasons. In some cases, such as after a
connection timeout, simply retrying a failed request is appropriate. The
`@retry <uplink.retry>` decorator can handle this for you:

``` python
from uplink import retry, Consumer, get

class GitHub(Consumer):
   @retry
   @get("user/{username}")
   def get_user(self, username):
      """Get user by username."""
```

Without any further configuration, the decorator will retry requests
that fail *for any reasons*. To constrain which exceptions should prompt
a retry attempt, use the `on_exception` argument:

``` python
from uplink import retry, Consumer, get

class GitHub(Consumer):
   # Retry only on failure to connect to the remote server.
   @retry(on_exception=retry.CONNECTION_TIMEOUT)
   @get("user/{username}")
   def get_user(self, username):
      """Get user by username."""
```

Further, as long as the expected exception is thrown, the decorator will
repeatedly retry until a response is rendered. If you'd like to cease
retrying after a specific number of attempts, use the `max_attempts`
argument:

``` python
from uplink import retry, Consumer, get

class GitHub(Consumer):
   # Try four times, then fail hard if no response.
   @retry(max_attempts=4)
   @get("user/{username}")
   def get_user(self, username):
      """Get user by username."""
```

The `@retry <uplink.retry>` decorators offers a bunch of other features!
Below is a contrived example... checkout the
`API documentation <retry_api>` for more:

``` python
from uplink import retry, Consumer, get

class GitHub(Consumer):
   @retry(
      # Retry on 503 response status code or any exception.
      when=retry.when.status(503) | retry.when.raises(Exception)
      # Stop after 5 attempts or when backoff exceeds 10 seconds.
      stop=retry.stop.after_attempt(5) | retry.stop.after_delay(10)
      # Use exponential backoff with added randomness.
      backoff=retry.backoff.jittered(multiplier=0.5)
   )
   @get("user/{username}")
   def get_user(self, username):
      """Get user by username."""
```

Finally, like other Uplink decorators, you can decorate a `Consumer`
subclass with `@retry <uplink.retry>` to `add retry support to all
methods of that class <decorate_consumer>`.

!!! note
Response and error handlers (see `here <custom response
handler>`) are invoked after the retry condition breaks or after all
retry attempts are exhausted, whatever comes first. These callbacks will
receive the first response/exception that triggers the retry's `stop`
condition or doesn't match its `when` filter.

## Client-Side Rate Limiting

Often, an organization may enforce a strict limit on the number of
requests a client can make to their public API within a fixed time
period (e.g., 15 calls every 15 minutes) to help prevent
denial-of-service (DoS) attacks and other issues caused by misbehaving
clients. On the client-side, we can avoid exceeding these server-side
limits by imposing our own rate limit.

The `@ratelimit` decorator enforces a constraint of *X calls every Y
seconds*:

``` python
from uplink import ratelimit, Consumer, get

class GitHub(Consumer):
   @ratelimit(calls=15, period=900)  # 15 calls every 15 minutes.
   @get("user/{username}")
   def get_user(self, username):
      """Get user by username."""
```

When the consumer reaches the limit, it will wait until the next period
before executing any subsequent requests. For blocking HTTP clients,
such as Requests, this means the main thread is blocked until then. On
the other hand, `using a non-blocking client <sync_vs_async>`, such as
`aiohttp`, enables you to continue making progress elsewhere while the
consumer waits for the current period to lapse.

Alternatively, you can fail fast when the limit is exceeded by setting
the `raise_on_limit` argument:

``` python
class GitHub(Consumer):
   # Raise Exception when the client exceeds the rate limit.
   @ratelimit(calls=15, period=900, raise_on_limit=Exception)
   @get("user/{username}")
   def get_user(self, username):
      """Get user by username."""
```

Like other Uplink decorators, you can decorate a `Consumer` subclass
with `@ratelimit <uplink.ratelimit>` to
`add rate limiting to all methods of that class <decorate_consumer>`.
