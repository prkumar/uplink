# Standard library imports
import collections
import sys

PY2 = False
PY3 = False

try:
    # Python 3.2+
    from inspect import signature

    PY3 = True
except ImportError:  # pragma: no cover
    # Python 2.7
    from inspect import getcallargs as get_call_args, getargspec as _getargspec

    PY2 = True

    def signature(_):
        raise ImportError

    def get_arg_spec(f):
        arg_spec = _getargspec(f)
        args = arg_spec.args
        if arg_spec.varargs is not None:
            args.append(arg_spec.varargs)
        if arg_spec.keywords is not None:
            args.append(arg_spec.keywords)
        return Signature(args, {}, None)
else:  # pragma: no cover
    def get_call_args(f, *args, **kwargs):
        sig = signature(f)
        arguments = sig.bind(*args, **kwargs).arguments
        # apply defaults:
        new_arguments = []
        for name, param in sig.parameters.items():
            try:
                new_arguments.append((name, arguments[name]))
            except KeyError:
                if param.default is not param.empty:
                    val = param.default
                elif param.kind is param.VAR_POSITIONAL:
                    val = ()
                elif param.kind is param.VAR_KEYWORD:
                    val = {}
                else:
                    continue
                new_arguments.append((name, val))
        return collections.OrderedDict(new_arguments)

    def get_arg_spec(f):
        sig = signature(f)
        parameters = sig.parameters
        args = []
        annotations = collections.OrderedDict()
        has_return_type = sig.return_annotation is not sig.empty
        return_type = sig.return_annotation if has_return_type else None
        for p in parameters:
            if parameters[p].annotation is not sig.empty:
                annotations[p] = parameters[p].annotation
            args.append(p)
        return Signature(args, annotations, return_type)

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse


Signature = collections.namedtuple(
    "Signature",
    "args annotations return_annotation"
)


if PY3:  # pragma: no cover
    def reraise(tp, value, tb=None):
        if value is None:
            value = tp()
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value
else:  # pragma: no cover
    def exec_(_code_, _globs_=None, _locs_=None):
        """Execute code in a namespace."""
        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")

    exec_("""def reraise(tp, value, tb=None):
    raise tp, value, tb
""")



