class AnnotationMeta(type):

    def __call__(cls, *args, **kwargs):
        if cls.can_be_static and cls.is_static_call(*args, **kwargs):
            self = super(AnnotationMeta, cls).__call__()
            self(args[0])
            return args[0]
        else:
            return super(AnnotationMeta, cls).__call__(*args, **kwargs)


class _Annotation(object):
    can_be_static = False

    def modify_request_definition(self, request_definition_builder):
        raise NotImplementedError

    @classmethod
    def is_static_call(cls, *args, **kwargs):
        try:
            is_builder = isinstance(args[0], RequestDefinitionBuilder)
        except IndexError:
            return False
        else:
            return is_builder and not (kwargs or args[1:])


Annotation = AnnotationMeta(
    "Annotation", (_Annotation,), {}
)


class AnnotationHandlerBuilder(object):
    __request_definition_builder = None

    def set_annotations(self, *annotations, **kwargs):
        for annotation in annotations:
            self.add_annotation(annotation)

    def add_annotation(self, annotation, *args, **kwargs):
        annotation.modify_request_definition(self.request_definition_builder)

    def set_request_definition_builder(self, request_definition_builder):
        if self.__request_definition_builder is None:
            self.__request_definition_builder = request_definition_builder

    @property
    def request_definition_builder(self):
        return self.__request_definition_builder

    def is_done(self):
        return True

    def build(self):
        raise NotImplementedError


class AnnotationHandler(object):

    @property
    def annotations(self):
        raise NotImplementedError


class UriDefinitionBuilder(object):

    @property
    def is_static(self):
        raise NotImplementedError

    @property
    def is_dynamic(self):
        raise NotImplementedError

    @is_dynamic.setter
    def is_dynamic(self, is_dynamic):
        raise NotImplementedError

    def add_variable(self, name):
        raise NotImplementedError

    @property
    def remaining_variables(self):
        raise NotImplementedError

    def build(self):
        raise NotImplementedError


class RequestDefinitionBuilder(object):

    @property
    def method(self):
        raise NotImplementedError

    @property
    def uri(self):
        raise NotImplementedError

    @property
    def argument_handler_builder(self):
        raise NotImplementedError

    @property
    def method_handler_builder(self):
        raise NotImplementedError

    def build(self):
        raise NotImplementedError


class RequestDefinition(object):

    @property
    def argument_annotations(self):
        raise NotImplementedError

    @property
    def method_annotations(self):
        raise NotImplementedError

    def define_request(self, request_builder, func_args, func_kwargs):
        raise NotImplementedError


class CallBuilder(object):

    @property
    def client(self):
        raise NotImplementedError

    @client.setter
    def client(self, client):
        raise NotImplementedError

    @property
    def base_url(self):
        raise NotImplementedError

    @base_url.setter
    def base_url(self, base_url):
        raise NotImplementedError

    @property
    def converter_factories(self):
        raise NotImplementedError


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
