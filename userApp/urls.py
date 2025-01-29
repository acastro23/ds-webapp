from django.urls import path
from .views import test_supabase


urlpatterns = [
    path("test-supabase/", test_supabase),  # URL for testing
]