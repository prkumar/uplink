# Third party imports
from twisted.internet import reactor, defer, task
from twisted.python import failure

# Local imports
from uplink.clients.io import interfaces


class TwistedStrategy(interfaces.ExecutionStrategy):
    _deferred = None

    def send(self, client, request, callback):
        deferred = client.send(request)
        deferred.addCallbacks(
            callback.on_success,
            lambda f: callback.on_failure(f.exc_type, f.exc_val, f.exc_tb),
        )
        return deferred

    def wait(self, duration, callback):
        return task.deferLater(reactor, duration, callback.on_success)

    def finish(self, response):
        self._deferred.callback(response)

    def fail(self, exc_type, exc_val, exc_tb):
        self._deferred.errback(failure.Failure(exc_val, exc_type, exc_tb))

    def execute(self, executable):
        self._deferred = defer.Deferred()
        executable.execute()
        return self._deferred
