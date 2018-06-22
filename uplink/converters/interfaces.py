class Converter(object):
    def convert(self, value):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        return self.convert(*args, **kwargs)

    def set_chain(self, chain):
        pass


class Factory(object):
    """
    An adapter that handles deserialization of HTTP request properties
    and serialization of HTTP response bodies using a particular
    protocol.
    """

    def create_response_body_converter(self, cls, request_definition):
        """
        Returns a callable that can convert a response body into the
        specified py:obj:`cls`.

        If this factory can't produce such a callable, it should return
        :py:obj:`None`, so another factory can have a chance to handle
        the type.
        """

    def create_request_body_converter(self, cls, request_definition):
        """
        Returns a callable that can convert `cls` into an acceptable
        request body.

        If this factory can't produce such a callable, it should return
        :py:obj:`None`, so another factory can have a chance to handle
        the type.
        """

    def create_string_converter(self, cls, request_definition):
        """
        Returns a callable that can convert `cls` into a
        :py:class:`str`.

        If this factory can't produce such a callable, it should return
        :py:obj:`None`, so another factory can have a chance to handle
        the type.
        """


class ConverterFactory(Factory):
    # TODO: Remove this in v1.0.0 -- use Factory instead.

    def create_response_body_converter(self, cls, request_definition):
        return self.make_response_body_converter(
            cls,
            request_definition.argument_annotations,
            request_definition.method_annotations,
        )

    def create_request_body_converter(self, cls, request_definition):
        return self.make_request_body_converter(
            cls,
            request_definition.argument_annotations,
            request_definition.method_annotations,
        )

    def create_string_converter(self, cls, request_definition):
        return self.make_string_converter(
            cls,
            request_definition.argument_annotations,
            request_definition.method_annotations,
        )

    def make_response_body_converter(
        self, type, argument_annotations, method_annotations
    ):
        pass

    def make_request_body_converter(
        self, type, argument_annotations, method_annotations
    ):
        pass

    def make_string_converter(
        self, type, argument_annotations, method_annotations
    ):
        pass
