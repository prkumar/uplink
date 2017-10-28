# Standard library imports
import collections

# Third party imports
import pytest

# Local imports
from uplink import backend, client, interfaces, helpers


@pytest.fixture
def http_client_mock(mocker):
    return mocker.Mock(spec=backend.interfaces.HttpClientAdapter)


@pytest.fixture
def request_mock(mocker):
    return mocker.Mock(spec=backend.interfaces.Request)


@pytest.fixture
def backend_mock(mocker):
    mock = mocker.Mock(spec=backend.interfaces.Backend)
    mock.make_backend.return_value = mock
    return mock


@pytest.fixture
def transaction_hook_mock(mocker):
    return mocker.Mock(spec=client.BaseTransactionHook)


@pytest.fixture
def converter_mock(mocker):
    return mocker.Mock(spec=interfaces.AbstractConverter)


@pytest.fixture
def converter_factory_mock(mocker):
    return mocker.Mock(spec=interfaces.AbstractConverterFactory)


@pytest.fixture
def annotation_mock(mocker):
    return mocker.Mock(spec=interfaces.AbstractAnnotation)


@pytest.fixture
def annotation_handler_builder_mock(mocker):
    return mocker.Mock(spec=interfaces.AbstractAnnotationHandlerBuilder)


@pytest.fixture
def annotation_handler_mock(mocker):
    return mocker.Mock(spec=interfaces.AbstractAnnotationHandler)


@pytest.fixture
def request_definition_builder(mocker):
    return mocker.Mock(spec=interfaces.AbstractRequestDefinitionBuilder)


@pytest.fixture
def request_definition(mocker):
    return mocker.Mock(spec=interfaces.AbstractRequestDefinition)


@pytest.fixture
def uplink_builder_mock(mocker):
    return mocker.Mock(spec=interfaces.AbstractUplinkBuilder)


@pytest.fixture
def request_builder(mocker):
    builder = mocker.MagicMock(spec=helpers.RequestBuilder)
    builder.info = collections.defaultdict(dict)
    return builder

