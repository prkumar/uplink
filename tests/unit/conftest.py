# Standard library imports
import collections

# Third-party imports
import pytest

# Local imports
from uplink import clients, converters, hooks, interfaces, helpers
from uplink.clients.exceptions import Exceptions


@pytest.fixture
def http_client_mock(mocker):
    client = mocker.Mock(spec=clients.interfaces.HttpClientAdapter)
    return client


@pytest.fixture
def transaction_hook_mock(mocker):
    return mocker.Mock(spec=hooks.TransactionHook)


@pytest.fixture
def converter_mock(mocker):
    return mocker.Mock(spec=converters.interfaces.Converter)


@pytest.fixture
def converter_factory_mock(mocker):
    return mocker.Mock(spec=converters.interfaces.Factory)


@pytest.fixture
def annotation_mock(mocker):
    return mocker.Mock(spec=interfaces.Annotation)


@pytest.fixture
def annotation_handler_builder_mock(mocker):
    return mocker.Mock(spec=interfaces.AnnotationHandlerBuilder)


@pytest.fixture
def annotation_handler_mock(mocker):
    return mocker.Mock(spec=interfaces.AnnotationHandler)


@pytest.fixture
def request_definition_builder(mocker):
    return mocker.Mock(spec=interfaces.RequestDefinitionBuilder)


@pytest.fixture
def request_definition(mocker):
    return mocker.Mock(spec=interfaces.RequestDefinition)


@pytest.fixture
def uplink_builder_mock(mocker):
    return mocker.Mock(spec=interfaces.CallBuilder)


@pytest.fixture
def request_builder(mocker):
    builder = mocker.MagicMock(spec=helpers.RequestBuilder)
    builder.info = collections.defaultdict(dict)
    builder.context = {}
    builder.get_converter.return_value = lambda x: x
    builder.client.exceptions = Exceptions()
    return builder
