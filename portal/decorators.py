from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(*roles):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            profile = getattr(request.user, "profile", None)
            role = "admin" if request.user.is_staff or request.user.is_superuser else (profile.role if profile else "student")
            if role not in roles:
                messages.error(request, "You do not have permission to access that page.")
                return redirect("dashboard")
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
