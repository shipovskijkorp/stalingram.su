from django.utils import timezone


class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(request, "user", None) is not None and request.user.is_authenticated:
            now = timezone.now()
            previous = request.session.get("stalingram_activity_touch", 0)
            if now.timestamp() - previous >= 45:
                type(request.user).objects.filter(pk=request.user.pk).update(last_seen_at=now)
                request.user.last_seen_at = now
                request.session["stalingram_activity_touch"] = int(now.timestamp())
        return self.get_response(request)
