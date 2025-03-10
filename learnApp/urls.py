from django.urls import path
from . import views


app_name = 'learnApp'

urlpatterns = [
    path('', views.learn_home, name='learn-home'),
    path('<str:algorithm_name>/', views.algorithm_detail, name='algorithm-detail'),
]
