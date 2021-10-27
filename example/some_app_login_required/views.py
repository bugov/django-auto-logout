from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm


class UserLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'login_page.html'


@login_required
def login_required_view(request):
    return render(request, 'login_required.html', {})
