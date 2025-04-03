from django.urls import path
from .views import register_user, login_user, logout_user, update_email, profile_page, profile_data
from django.shortcuts import render


app_name = "userApp"

urlpatterns = [                             
    path("register/", register_user, name="register-user"),
    path("login/", login_user, name="login-user"),
    path("update-email/", update_email, name="update-email"),
    path("logout/", logout_user, name="logout-user"),
    path("login-page/", lambda request: render(request, "userApp/login.html"), name="login-page"),
    path("register-page/", lambda request: render(request, "userApp/register.html"), name="register-page"),
    path("profile-page/", profile_page, name="profile-page"),
    path("profile-data/", profile_data, name="profile-data"),
]