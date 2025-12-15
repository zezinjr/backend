from functools import WRAPPER_ASSIGNMENTS, wraps

from account import exceptions


def permission_required(*permissions, fn=None):
    def decorator(view):
        @wraps(view, assigned=WRAPPER_ASSIGNMENTS)
        def wrapped_view(self, request, *args, **kwargs):

            if callable(fn):
                obj = fn(request, *args, **kwargs)
            else:
                obj = fn

            missing_permissions = [perm for perm in permissions
                                   if not request.user.has_perm(perm, obj)]

            if any(missing_permissions):
                raise exceptions.PermissionNotAllowedException()

            return view(self, request, *args, **kwargs)

        return wrapped_view

    return decorator


def disable_for_loaddata(signal_handler):
    """Decorator that turns off signal handlers when loading fixture data.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if 'raw' in kwargs:
            if kwargs['raw']:
                return
        signal_handler(*args, **kwargs)

    return wrapper


def strong_receiver(signal, **kwargs):
    def _decorator(func):
        if 'weak' not in kwargs:
            kwargs['weak'] = False
        if isinstance(signal, (list, tuple)):
            for s in signal:
                s.connect(func, **kwargs)
        else:
            signal.connect(func, **kwargs)
        return func

    return _decorator


def skip_signal(signal_handler):
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if 'instance' in kwargs:
            instance = kwargs.get('instance')
            if hasattr(instance, 'skip_signal'):
                if getattr(instance, 'skip_signal'):
                    return
        signal_handler(*args, **kwargs)

    return wrapper
