class Converter(object):

    def convert(self, value):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        return self.convert(*args, **kwargs)

    def set_chain(self, chain):
        pass


class ConverterFactory(object):
    """
    An adapter that handles deserialization of HTTP request properties
    and serialization of HTTP response bodies using a particular
    protocol.
    """

    def make_response_body_converter(self, type, argument_annotations,
                                     method_annotations):
        """
        Returns a callable that can convert a response body into the
        specified py:obj:`type`.

        If this factory can't produce such a callable, it should return
        :py:obj:`None`, so another factory can have a chance to handle
        the type.
        """

    def make_request_body_converter(self, type, argument_annotations,
                                    method_annotations):
        """
        Returns a callable that can convert `type` into an acceptable
        request body.

        If this factory can't produce such a callable, it should return
        :py:obj:`None`, so another factory can have a chance to handle
        the type.
        """

    def make_string_converter(self, type, argument_annotations,
                              method_annotations):
        """
        Returns a callable that can convert `type` into a
        :py:class:`str`.

        If this factory can't produce such a callable, it should return
        :py:obj:`None`, so another factory can have a chance to handle
        the type.
        """
