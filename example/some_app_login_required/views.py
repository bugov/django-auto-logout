from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def login_page(request):
    return render(request, 'login_page.html', {})


@login_required
def login_required_view(request):
    return render(request, 'login_required.html', {})
