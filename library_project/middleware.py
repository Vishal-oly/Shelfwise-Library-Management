from urllib.parse import urlsplit

from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden


class PreviewOriginProtectionMiddleware:
    """Cookie-less CSRF mitigation for the embedded Arena preview only."""

    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method not in self.SAFE_METHODS:
            origin = request.headers.get("Origin", "")
            parsed = urlsplit(origin)
            try:
                host = request.get_host()
            except Exception:
                return HttpResponseForbidden("Request host is not allowed.")
            if parsed.scheme != "https" or parsed.netloc.lower() != host.lower():
                return HttpResponseForbidden("Request origin is not allowed.")
        return self.get_response(request)


class PreviewGuestMiddleware:
    """Give the embedded preview a demo identity when browser cookies are blocked.

    This middleware is installed only when SHELFWISE_PREVIEW=1. The normal
    local/deployed app continues to require Django authentication and sessions.
    """

    PUBLIC_PATHS = {"/", "/signup/", "/login/"}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path not in self.PUBLIC_PATHS and not request.user.is_authenticated:
            User = get_user_model()
            guest, _ = User.objects.get_or_create(
                username="shelfwise_guest",
                defaults={"first_name": "Shelfwise Guest", "is_active": True},
            )
            request.user = guest
        return self.get_response(request)
