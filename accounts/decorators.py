from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

def role_required(*allowed_roles):
    """
    Decorator for views that checks whether a user has one of the specified roles.
    If the user isn't logged in, redirects to settings.LOGIN_URL with ?next=...
    If the user doesn't have the required role, raises PermissionDenied (HTTP 403).
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                login_url = reverse('accounts:login')
                return redirect(f"{login_url}?next={request.path}")
            
            user_role = getattr(request.user, 'role', None)
            is_admin = getattr(request.user, 'is_admin', False)

            # Admins have access to ADMIN routes and can supervise other routes if permitted
            if 'ADMIN' in allowed_roles and (user_role == 'ADMIN' or request.user.is_superuser):
                return view_func(request, *args, **kwargs)

            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(
                request,
                f"Access denied: This section is restricted to {', '.join(allowed_roles)} accounts."
            )
            raise PermissionDenied(f"User role '{user_role}' not authorized for this resource.")
        return _wrapped_view
    return decorator
