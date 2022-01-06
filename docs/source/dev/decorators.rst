Decorators
**********

The method decorators detailed in this section describe request properties that
are relevant to all invocations of a consumer method.

headers
=======

.. autoclass:: uplink.headers


params
======

.. autoclass:: uplink.params

json
====

.. autoclass:: uplink.json

form_url_encoded
================

.. autoclass:: uplink.form_url_encoded

multipart
=========

.. autoclass:: uplink.multipart

timeout
=======

.. autoclass:: uplink.timeout

args
====

.. autoclass:: uplink.args

response_handler
================

.. autoclass:: uplink.response_handler

error_handler
=============

.. autoclass:: uplink.error_handler

inject
======

.. autoclass:: uplink.inject


returns.*
=========

Converting an HTTP response body into a custom Python object is
straightforward with Uplink; the :py:mod:`uplink.returns` modules
exposes optional decorators for defining the expected return type and
data serialization format for any consumer method.

.. automodule:: uplink.returns
    :members:

.. _retry_api:

retry
=====

.. automodule:: uplink.retry
    :members:

retry.when
----------

The default behavior of the :class:`~uplink.retry` decorator is to retry on
any raised exception. To override the retry criteria, use the :mod:`~uplink.retry`
decorator's ``when`` argument to specify a retry condition exposed through the
:mod:`uplink.retry.when` module:

.. code-block:: python
   :emphasize-lines: 1,4-5

    from uplink.retry.when import raises

    class GitHub(uplink.Consumer):
        # Retry when a client connection timeout occurs
        @uplink.retry(when=raises(retry.CONNECTION_TIMEOUT))
        @uplink.get("/users/{user}")
        def get_user(self, user):
            """Get user by username."""

Use the ``|`` operator to logically combine retry conditions:

.. code-block:: python
   :emphasize-lines: 1,4-5

    from uplink.retry.when import raises, status

    class GitHub(uplink.Consumer):
        # Retry when an exception is raised or the status code is 503
        @uplink.retry(when=raises(Exception) | status(503))
        @uplink.get("/users/{user}")
        def get_user(self, user):
            """Get user by username."""

.. automodule:: uplink.retry.when
    :members:

retry.backoff
-------------

Retrying failed requests typically involves backoff: the client can wait
some time before the next retry attempt to avoid high contention on the remote
service.

To this end, the :class:`~uplink.retry` decorator uses `capped
exponential backoff with jitter
<https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/>`_
by default, To override this, use the decorator's ``backoff`` argument
to specify one of the alternative approaches exposed through the
:mod:`uplink.retry.backoff` module:

.. code-block:: python
   :emphasize-lines: 2,5-6

   from uplink import retry, Consumer, get
   from uplink.retry.backoff import fixed

   class GitHub(Consumer):
      # Employ a fixed one second delay between retries.
      @retry(backoff=fixed(1))
      @get("user/{username}")
      def get_user(self, username):
         """Get user by username."""

.. code-block:: python
   :emphasize-lines: 4

    from uplink.retry.backoff import exponential

    class GitHub(uplink.Consumer):
        @uplink.retry(backoff=exponential(multiplier=0.5))
        @uplink.get("/users/{user}")
        def get_user(self, user):
            """Get user by username."""

You can implement a custom backoff strategy by extending the class
:class:`uplink.retry.RetryBackoff`:

.. code-block:: python
   :emphasize-lines: 3,7

    from uplink.retry import RetryBackoff

    class MyCustomBackoff(RetryBackoff):
        ...

    class GitHub(uplink.Consumer):
        @uplink.retry(backoff=MyCustomBackoff())
        @uplink.get("/users/{user}")
        def get_user(self, user):
            pass

.. automodule:: uplink.retry.backoff
    :members:

retry.stop
----------

By default, the :mod:`~uplink.retry` decorator will repeatedly retry the
original request until a response is rendered. To override this behavior,
use the :mod:`~uplink.retry` decorator's ``stop`` argument to specify one
of the strategies exposed in the :mod:`uplink.retry.stop` module:

.. code-block:: python
   :emphasize-lines: 1,4

    from uplink.retry.stop import after_attempt

    class GitHub(uplink.Consumer):
        @uplink.retry(stop=after_attempt(3))
        @uplink.get("/users/{user}")
        def get_user(self, user):

Use the ``|`` operator to logically combine strategies:

.. code-block:: python
   :emphasize-lines: 1,4-5

    from uplink.retry.stop import after_attempt, after_delay

    class GitHub(uplink.Consumer):
        # Stop after 3 attempts or after the backoff exceeds 10 seconds.
        @uplink.retry(stop=after_attempt(3) | after_delay(10))
        @uplink.get("/users/{user}")
        def get_user(self, user):
            pass

.. automodule:: uplink.retry.stop
    :members:

.. autodata:: uplink.retry.stop.NEVER
   :annotation:

ratelimit
=========

.. autoclass:: uplink.ratelimit


.. autoclass:: uplink.ratelimit.RateLimitExceeded
