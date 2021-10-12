from django.contrib import admin
from django.urls import path

from some_app_login_required.views import login_page, login_required_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_page),
    path('login-required/', login_required_view),
]
