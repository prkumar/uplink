# Decorators

The method decorators detailed in this section describe request properties that
are relevant to all invocations of a consumer method.

::: uplink.headers
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.params
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.json
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.form_url_encoded
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.multipart
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.timeout
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.args
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.response_handler
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.error_handler
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.inject
    options:
        show_bases: false
        members: false
        inherited_members: false

## HTTP Method Decorators

These decorators define the HTTP method to use for a request.

::: uplink.get
::: uplink.post
::: uplink.put
::: uplink.patch
::: uplink.delete
::: uplink.head

## `returns.*`

Converting an HTTP response body into a custom Python object is
straightforward with Uplink; the `uplink.returns` modules exposes
optional decorators for defining the expected return type and data
serialization format for any consumer method.

::: uplink.returns.json
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.returns.from_json
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.returns.schema
    options:
        show_bases: false
        members: false
        inherited_members: false

## `retry.*`

::: uplink.retry
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.retry.RetryBackoff
    options:
        show_bases: false
        members: false
        inherited_members: false

## `retry.when`

The default behavior of the `uplink.retry` decorator is to retry on any
raised exception. To override the retry criteria, use the
`uplink.retry` decorator's `when` argument to specify a retry condition
exposed through the `uplink.retry.when` module:

``` python
from uplink.retry.when import raises

class GitHub(uplink.Consumer):
    # Retry when a client connection timeout occurs
    @uplink.retry(when=raises(retry.CONNECTION_TIMEOUT))
    @uplink.get("/users/{user}")
    def get_user(self, user):
        """Get user by username."""
```

Use the `|` operator to logically combine retry conditions:

``` python
from uplink.retry.when import raises, status

class GitHub(uplink.Consumer):
    # Retry when an exception is raised or the status code is 503
    @uplink.retry(when=raises(Exception) | status(503))
    @uplink.get("/users/{user}")
    def get_user(self, user):
        """Get user by username."""
```

::: uplink.retry.when.raises
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.retry.when.status
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.retry.when.status_5xx
    options:
        show_bases: false
        members: false
        inherited_members: false

## `retry.backoff`

Retrying failed requests typically involves backoff: the client can wait
some time before the next retry attempt to avoid high contention on the
remote service.

To this end, the `uplink.retry` decorator uses [capped exponential
backoff with
jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
by default, To override this, use the decorator's `backoff` argument to
specify one of the alternative approaches exposed through the
`uplink.retry.backoff` module:

``` python
from uplink import retry, Consumer, get
from uplink.retry.backoff import fixed

class GitHub(Consumer):
   # Employ a fixed one second delay between retries.
   @retry(backoff=fixed(1))
   @get("user/{username}")
   def get_user(self, username):
      """Get user by username."""
```

``` python
from uplink.retry.backoff import exponential

class GitHub(uplink.Consumer):
    @uplink.retry(backoff=exponential(multiplier=0.5))
    @uplink.get("/users/{user}")
    def get_user(self, user):
        """Get user by username."""
```

You can implement a custom backoff strategy by extending the class
`uplink.retry.RetryBackoff`:

``` python
from uplink.retry import RetryBackoff

class MyCustomBackoff(RetryBackoff):
    ...

class GitHub(uplink.Consumer):
    @uplink.retry(backoff=MyCustomBackoff())
    @uplink.get("/users/{user}")
    def get_user(self, user):
        pass
```

::: uplink.retry.backoff.jittered
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.retry.backoff.exponential
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.retry.backoff.fixed
    options:
        show_bases: false
        members: false
        inherited_members: false

## retry.stop

By default, the `uplink.retry` decorator will repeatedly retry the
original request until a response is rendered. To override this
behavior, use the `uplink.retry` decorator's `stop` argument to specify
one of the strategies exposed in the `uplink.retry.stop` module:

``` python
from uplink.retry.stop import after_attempt

class GitHub(uplink.Consumer):
    @uplink.retry(stop=after_attempt(3))
    @uplink.get("/users/{user}")
    def get_user(self, user):
```

Use the `|` operator to logically combine strategies:

``` python
from uplink.retry.stop import after_attempt, after_delay

class GitHub(uplink.Consumer):
    # Stop after 3 attempts or after the backoff exceeds 10 seconds.
    @uplink.retry(stop=after_attempt(3) | after_delay(10))
    @uplink.get("/users/{user}")
    def get_user(self, user):
        pass
```

::: uplink.retry.stop.after_attempt
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.retry.stop.after_delay
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.retry.stop.NEVER
    options:
        show_bases: false
        members: false
        inherited_members: false

## `ratelimit`

::: uplink.ratelimit.ratelimit
    options:
        show_bases: false
        members: false
        inherited_members: false

::: uplink.ratelimit.RateLimitExceeded
    options:
        show_bases: false
        members: false
        inherited_members: false
