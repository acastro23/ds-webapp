from django.urls import path
from . import views

app_name = 'timeTrialApp'

urlpatterns = [
    path('', views.time_trial_home, name="time-trial-home"),
    path('start/', views.time_trial_start, name="time-trial-start"),
    path('submit/', views.time_trial_submit, name="time-trial-submit"),
]
