class Converter(object):

    def convert(self, value):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        return self.convert(*args, **kwargs)


class ConverterFactory(object):

    def make_response_body_converter(self, type_, argument_annotations,
                                     method_annotations):
        pass

    def make_request_body_converter(self, type_, argument_annotations,
                                    method_annotations):
        pass

    def make_string_converter(self, type_, argument_annotations,
                              method_annotations):
        pass


class RequiresChain(object):

    def set_chain(self, chain):
        raise NotImplementedError
