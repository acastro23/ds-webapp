from django.urls import path
from . import views


app_name = "leaderboardApp"

urlpatterns = [
    path('', views.leaderboard_main, name="leaderboard-home"),
]
