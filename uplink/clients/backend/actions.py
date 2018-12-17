# Local imports
from uplink.clients.backend import state


def wait(seconds):
    def action(previous_state):
        return state.WaitState(previous_state.request, seconds)

    return action


def send(request):
    def action(_):
        return state.SendRequest(request)

    return action


def finish(response):
    def action(previous_state):
        return state.Finish(previous_state.request, response)

    return action


def fail(exc_type, exc_val, exc_tb):
    def action(previous_state):
        return state.Fail(previous_state.request, exc_type, exc_val, exc_tb)

    return action


def prepare(request):
    def action(_):
        return state.BeforeRequest(request)

    return action
