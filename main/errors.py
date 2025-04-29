from django.shortcuts import render

def custom_400(request, exception):
    context = {}
    response = render(request, "main/errors/400.html", context=context)
    response.status_code = 400
    return response


def custom_403(request, exception):
    context = {}
    response = render(request, "main/errors/403.html", context=context)
    response.status_code = 403
    return response


def custom_404(request, exception):
    context = {}
    response = render(request, "main/errors/404.html", context=context)
    response.status_code = 404
    return response


def custom_500(request):
    context = {}
    response = render(request, "main/errors/500.html", context=context)
    response.status_code = 500
    return response