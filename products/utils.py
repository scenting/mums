from django.http import HttpResponse
from django.core import urlresolvers


def html_decorator(func):
    """
    This decorator wraps the output in html.
    """

    def _decorated(*args, **kwargs):
        response = func(*args, **kwargs)

        wrapped = ("<html><body>",
                   response.content,
                   "</body></html>")

        return HttpResponse(wrapped)

    return _decorated


@html_decorator
def debug(request):
    """
    Debug endpoint that uses the html_decorator
    """
    path = request.META.get("PATH_INFO")
    api_url = path.replace("debug/", "")

    view = urlresolvers.resolve(api_url)

    accept = request.META.get("HTTP_ACCEPT")
    accept += ",application/json"
    request.META["HTTP_ACCEPT"] = accept

    res = view.func(request, **view.kwargs)
    return HttpResponse(res._container)
