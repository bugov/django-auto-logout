from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def login_page(request):
    return HttpResponse(b'login page')


@login_required
def login_required_view(request):
    return HttpResponse(b'login required view')
