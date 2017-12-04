class Converter(object):

    def convert(self, value):
        raise NotImplementedError


class ConverterFactory(object):

    def make_response_body_converter(self, type_, argument_annotations,
                                     method_annotations):
        raise NotImplementedError

    def make_request_body_converter(self, type_, argument_annotations,
                                    method_annotations):
        raise NotImplementedError

    def make_string_converter(self, type_, argument_annotations,
                              method_annotations):
        raise NotImplementedError
