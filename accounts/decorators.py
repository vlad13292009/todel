from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role != role:
                raise PermissionDenied("Доступ запрещён")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def organizer_required(view_func):
    return role_required('organizer')(view_func)


def participant_required(view_func):
    return role_required('participant')(view_func)
