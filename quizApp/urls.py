from django.urls import path
from . import views

app_name = 'quizApp'

urlpatterns = [
    path('', views.quiz_home, name="quiz-home"),
    path('<int:quiz_id>/', views.quiz_detail, name="quiz-detail"),
    path('<int:quiz_id>/start/', views.quiz_start, name="quiz-start"),
    path('<int:quiz_id>/submit/', views.quiz_submit, name='quiz-submit'),
    path('<int:quiz_id>/results/<int:score>/', views.quiz_results, name='quiz-results'),
]