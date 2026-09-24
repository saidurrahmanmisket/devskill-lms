import time
from django.conf import settings
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

class InactivityTimeoutMiddleware:
    """
    FR-AUTH-04: Invalidate session cookies upon manual sign-out, browser closure,
    or after 30 minutes (1800 seconds) of continuous inactivity.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = getattr(settings, 'INACTIVITY_TIMEOUT_SECONDS', 1800)

    def __call__(self, request):
        if request.user.is_authenticated:
            current_time = time.time()
            last_activity = request.session.get('last_activity')

            if last_activity is not None:
                elapsed = current_time - last_activity
                if elapsed > self.timeout:
                    logout(request)
                    request.session.flush()
                    messages.warning(
                        request,
                        "Your session has expired due to 30 minutes of inactivity. Please log in again."
                    )
                    login_url = reverse('accounts:login')
                    return redirect(f"{login_url}?next={request.path}")

            request.session['last_activity'] = current_time

        response = self.get_response(request)
        return response
