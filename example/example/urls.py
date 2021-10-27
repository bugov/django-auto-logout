from django.contrib import admin
from django.urls import path

from some_app_login_required.views import UserLoginView, login_required_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', UserLoginView.as_view()),
    path('login-required/', login_required_view),
]
