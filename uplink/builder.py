# Standard library imports
import functools
import warnings

# Local imports
from uplink import (
    arguments,
    auth as auth_,
    clients,
    converters as converters_,
    exceptions,
    helpers,
    hooks as hooks_,
    interfaces,
    session,
    utils,
)

__all__ = ["build", "Consumer"]


class RequestPreparer(object):
    def __init__(self, builder, consumer=None):
        self._hooks = list(builder.hooks)
        self._client = builder.client
        self._base_url = str(builder.base_url)
        self._converters = list(builder.converters)
        self._auth = builder.auth
        self._consumer = consumer

    def _join_url_with_base(self, url):
        return utils.urlparse.urljoin(self._base_url, url)

    def _get_hook_chain(self, contract):
        chain = list(contract.transaction_hooks)
        if callable(contract.return_type):
            chain.append(hooks_.ResponseHandler(contract.return_type))
        chain.extend(self._hooks)
        return chain

    def _wrap_hook(self, func):
        return functools.partial(func, self._consumer)

    def apply_hooks(self, chain, request_builder, sender):
        hook = hooks_.TransactionHookChain(*chain)
        hook.audit_request(self._consumer, request_builder)
        if hook.handle_response is not None:
            sender.add_callback(self._wrap_hook(hook.handle_response))
        sender.add_exception_handler(self._wrap_hook(hook.handle_exception))

    def prepare_request(self, request_builder):
        request_builder.url = self._join_url_with_base(request_builder.url)
        self._auth(request_builder)
        sender = self._client.create_request()
        chain = self._get_hook_chain(request_builder)
        if chain:
            self.apply_hooks(chain, request_builder, sender)
        return sender.send(
            request_builder.method, request_builder.url, request_builder.info
        )

    def create_request_builder(self, definition):
        registry = definition.make_converter_registry(self._converters)
        return helpers.RequestBuilder(registry)


class CallFactory(object):
    def __init__(self, request_preparer, request_definition):
        self._request_preparer = request_preparer
        self._request_definition = request_definition

    def __call__(self, *args, **kwargs):
        builder = self._request_preparer.create_request_builder(
            self._request_definition
        )
        self._request_definition.define_request(builder, args, kwargs)
        return self._request_preparer.prepare_request(builder)


class Builder(interfaces.CallBuilder):
    """The default callable builder."""

    def __init__(self):
        self._base_url = ""
        self._hooks = []
        self._client = clients.get_client()
        self._converters = converters_.get_default_converter_factories()
        self._auth = auth_.get_auth()

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, client):
        if client is not None:
            self._client = clients.get_client(client)

    @property
    def hooks(self):
        return iter(self._hooks)

    def add_hook(self, *hooks):
        self._hooks.extend(hooks)

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, base_url):
        self._base_url = base_url

    @property
    def converters(self):
        return self._converters

    @converters.setter
    def converters(self, converters):
        if isinstance(converters, converters_.interfaces.Factory):
            converters = (converters,)
        self._converters = tuple(converters)
        self._converters += converters_.get_default_converter_factories()

    @property
    def auth(self):
        return self._auth

    @auth.setter
    def auth(self, auth):
        if auth is not None:
            self._auth = auth_.get_auth(auth)

    def build(self, definition, consumer=None):
        """
        Creates a callable that uses the provided definition to execute
        HTTP requests when invoked.
        """
        return CallFactory(RequestPreparer(self, consumer), definition)


class ConsumerMethod(object):
    """
    A wrapper around a :py:class`interfaces.RequestDefinitionBuilder`
    instance bound to a :py:class:`Consumer` subclass, mainly responsible
    for controlling access to the instance.
    """

    def __init__(self, owner_name, attr_name, request_definition_builder):
        self._request_definition_builder = request_definition_builder
        self._owner_name = owner_name
        self._attr_name = attr_name
        self._request_definition = self._build_definition()

    def _build_definition(self):
        try:
            return self._request_definition_builder.build()
        except exceptions.InvalidRequestDefinition as error:
            # TODO: Find a Python 2.7 compatible way to reraise
            raise exceptions.UplinkBuilderError(
                self._owner_name, self._attr_name, error
            )

    def __get__(self, instance, owner):
        if instance is None:
            return self._request_definition_builder
        else:
            return instance.session.create(instance, self._request_definition)


class ConsumerMeta(type):
    @staticmethod
    def _wrap_if_definition(cls_name, key, value):
        if isinstance(value, interfaces.RequestDefinitionBuilder):
            value = ConsumerMethod(cls_name, key, value)
        return value

    @staticmethod
    def _set_init_handler(namespace):
        try:
            init = namespace["__init__"]
        except KeyError:
            pass
        else:
            builder = arguments.ArgumentAnnotationHandlerBuilder.from_func(init)
            handler = builder.build()

            @functools.wraps(init)
            def new_init(self, *args, **kwargs):
                init(self, *args, **kwargs)
                call_args = utils.get_call_args(init, self, *args, **kwargs)
                f = functools.partial(
                    handler.handle_call_args, call_args=call_args
                )
                hook = hooks_.RequestAuditor(f)
                self.session.inject(hook)

            namespace["__init__"] = new_init

    def __new__(mcs, name, bases, namespace):
        mcs._set_init_handler(namespace)

        # Wrap all definition builders with a special descriptor that
        # handles attribute access behavior.
        for key, value in namespace.items():
            namespace[key] = mcs._wrap_if_definition(name, key, value)
        return super(ConsumerMeta, mcs).__new__(mcs, name, bases, namespace)

    def __setattr__(cls, key, value):
        value = cls._wrap_if_definition(cls.__name__, key, value)
        super(ConsumerMeta, cls).__setattr__(key, value)


_Consumer = ConsumerMeta("_Consumer", (), {})


class Consumer(interfaces.Consumer, _Consumer):
    """
    Base consumer class with which to define custom consumers.

    Example usage:

    .. code-block:: python

        from uplink import Consumer, get

        class GitHub(Consumer):

            @get("/users/{user}")
            def get_user(self, user):
                pass

        client = GitHub("https://api.github.com/")
        client.get_user("prkumar").json()  # {'login': 'prkumar', ... }

    Args:
        base_url (:obj:`str`, optional): The base URL for any request
            sent from this consumer instance.
        client (optional): A supported HTTP client instance (e.g.,
            a :class:`requests.Session`) or an adapter (e.g.,
            :class:`~uplink.RequestsClient`).
        converters (:class:`ConverterFactory`, optional):
            One or more objects that encapsulate custom
            (de)serialization strategies for request properties and/or
            the response body. (E.g.,
            :class:`~uplink.converters.MarshmallowConverter`)
        auth (:obj:`tuple` or :obj:`callable`, optional): The
            authentication object for this consumer instance.
        hooks (:class:`~uplink.hooks.TransactionHook`, optional):
            One or more hooks to modify behavior of request execution
            and response handling (see :class:`~uplink.response_handler`
            or :class:`~uplink.error_handler`).
    """

    def __init__(
        self,
        base_url="",
        client=None,
        converters=(),
        auth=None,
        hooks=(),
        **kwargs
    ):
        builder = Builder()
        builder.base_url = base_url
        builder.converters = kwargs.pop("converter", converters)
        hooks = kwargs.pop("hook", hooks)
        if isinstance(hooks, hooks_.TransactionHook):
            hooks = (hooks,)
        builder.add_hook(*hooks)
        builder.auth = auth
        builder.client = client
        self.__session = session.Session(builder)
        self.__client = builder.client

    def _inject(self, hook, *more_hooks):
        self.session.inject(hook, *more_hooks)

    @property
    def session(self):
        """
        The :class:`~uplink.session.Session` object for this consumer
        instance.

        Exposes the configuration of this :class:`~uplink.Consumer`
        instance and allows the persistence of certain properties across
        all requests sent from that instance.

        Example usage:

        .. code-block:: python

            import uplink

            class MyConsumer(uplink.Consumer):
                def __init__(self, language):
                    # Set this header for all requests of the instance.
                    self.session.headers["Accept-Language"] = language
                    ...

        Returns:
            :class:`~uplink.session.Session`
        """
        return self.__session

    @property
    def exceptions(self):
        """
        An enum of standard HTTP client exceptions that can be handled.

        This property enables the handling of specific exceptions from
        the backing HTTP client.

        Example:

            .. code-block:: python

                try:
                    github.get_user(user_id)
                except github.exceptions.ServerTimeout:
                    # Handle the timeout of the request
                    ...
        """
        return self.__client.exceptions


def build(service_cls, *args, **kwargs):
    name = service_cls.__name__
    warnings.warn(
        "`uplink.build` is deprecated and will be removed in v1.0.0. "
        "To construct a consumer instance, have `{0}` inherit "
        "`uplink.Consumer` then instantiate (e.g., `{0}(...)`). ".format(name),
        DeprecationWarning,
    )
    consumer = type(name, (service_cls, Consumer), dict(service_cls.__dict__))
    return consumer(*args, **kwargs)
