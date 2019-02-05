# Third-party imports
import pytest

# Local imports
from uplink.clients.io import interfaces, state, transitions


@pytest.fixture
def request_execution_mock(mocker):
    return mocker.Mock(spec=interfaces.RequestExecution)


@pytest.fixture
def request_state_mock(mocker):
    return mocker.Mock(spec=interfaces.RequestState)


class BasicStateTest(object):
    def create_state(self, request):
        raise NotImplementedError

    @staticmethod
    def _create_request_mock():
        return object()

    def test_prepare(self):
        request = self._create_request_mock()
        target = self.create_state(request)
        output = target.prepare(request)
        assert output == state.BeforeRequest(request)

    def test_send(self):
        request = self._create_request_mock()
        target = self.create_state(request)
        output = target.send(request)
        assert output == state.SendRequest(request)

    def test_fail(self):
        request = self._create_request_mock()
        target = self.create_state(request)
        error = Exception()
        output = target.fail(Exception, error, None)
        assert output == state.Fail(request, Exception, error, None)

    def test_finish(self):
        request = self._create_request_mock()
        response = object()
        target = self.create_state(request)
        output = target.finish(response)
        assert output == state.Finish(request, response)

    def test_sleep(self):
        request = self._create_request_mock()
        target = self.create_state(request)
        output = target.sleep(10)
        assert output == state.Sleep(request, 10)

    def test_request_property(self):
        request = self._create_request_mock()
        target = self.create_state(request)
        assert target.request == request


class TestBeforeRequest(BasicStateTest):
    def create_state(self, request):
        return state.BeforeRequest(request)


class TestAfterResponse(BasicStateTest):
    def create_state(self, request):
        return state.AfterResponse(request, object())


class TestAfterException(BasicStateTest):
    def create_state(self, request):
        return state.AfterException(request, Exception, Exception(), None)


class TestSleep(object):
    def test_execute(self, request_execution_mock):
        request = object()
        sleep = state.Sleep(request, 10)
        sleep.execute(request_execution_mock)
        assert request_execution_mock.sleep.called

        args, _ = request_execution_mock.sleep.call_args
        callback = args[1]
        assert isinstance(callback, interfaces.SleepCallback)

        callback.on_success()
        assert request_execution_mock.state == state.BeforeRequest(request)

        error = Exception()
        callback.on_failure(Exception, error, None)
        assert request_execution_mock.state == state.AfterException(
            request, Exception, error, None
        )


class TestSendRequest(object):
    def test_execute(self, request_execution_mock):
        request = object()
        send_request = state.SendRequest(request)
        send_request.execute(request_execution_mock)
        assert request_execution_mock.send.called

        args, _ = request_execution_mock.send.call_args
        callback = args[1]
        assert isinstance(callback, interfaces.InvokeCallback)

        response = object()
        callback.on_success(response)
        assert request_execution_mock.state == state.AfterResponse(
            request, response
        )

        error = Exception()
        callback.on_failure(Exception, error, None)
        assert request_execution_mock.state == state.AfterException(
            request, Exception, error, None
        )


class TestFail(object):
    def test_execute(self, request_execution_mock):
        request, error = object(), Exception()
        fail = state.Fail(request, type(error), error, None)
        fail.execute(request_execution_mock)
        request_execution_mock.fail.assert_called_with(Exception, error, None)


class TestFinish(object):
    def test_execute(self, request_execution_mock):
        request, response = object(), object()
        finish = state.Finish(request, response)
        finish.execute(request_execution_mock)
        request_execution_mock.finish.assert_called_with(response)


def test_sleep_transition(request_state_mock):
    transitions.sleep(10)(request_state_mock)
    request_state_mock.sleep.assert_called_with(10)


def test_send_transition(request_state_mock):
    request = object()
    transitions.send(request)(request_state_mock)
    request_state_mock.send.assert_called_with(request)


def test_finish_transition(request_state_mock):
    response = object()
    transitions.finish(response)(request_state_mock)
    request_state_mock.finish.assert_called_with(response)


def test_fail_transition(request_state_mock):
    error = Exception()
    transitions.fail(Exception, error, None)(request_state_mock)
    request_state_mock.fail.assert_called_with(Exception, error, None)


def test_prepare_transition(request_state_mock):
    request = object()
    transitions.prepare(request)(request_state_mock)
    request_state_mock.prepare.assert_called_with(request)
