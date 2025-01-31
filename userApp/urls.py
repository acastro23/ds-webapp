from django.urls import path
from .views import test_supabase, register_user, login_user, logout_user, update_email


app_name = "userApp"

urlpatterns = [
    path("test-supabase/", test_supabase),                              # URL for testing
    path("register/", register_user, name="register-user"),
    path("login/", login_user, name="login-user"),
    path("update-email/", update_email, name="update-email"),
    path("logout/", logout_user, name="logout-user"),
]