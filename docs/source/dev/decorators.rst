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


retry
=====

.. automodule:: uplink.retry
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
   from uplink.retry import backoff

   class GitHub(Consumer):
      # Employ a fixed one second delay between retries.
      @retry(backoff=backoff.fixed(1))
      @get("user/{username}")
      def get_user(self, username):
         """Get user by username."""

.. code-block:: python
   :emphasize-lines: 4

    from uplink.retry import backoff

    class GitHub(uplink.Consumer):
        @uplink.retry(backoff=backoff.exponential(multiplier=0.5))
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

    from uplink.retry import stop

    class GitHub(uplink.Consumer):
        @uplink.retry(stop=stop.after_attempts(3))
        @uplink.get("/users/{user}")
        def get_user(self, user):

.. automodule:: uplink.retry.stop
    :members:

ratelimit
=========

.. autoclass:: uplink.ratelimit
