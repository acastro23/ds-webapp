from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse

# Create your views here.
def time_trial_home(request):
    return render(request, 'timeTrialApp/time_trial_home.html')


def time_trial_start(request):
    """AC02152025 -- Here we randomly select questions from all quizzes and starts the Time Trial."""
    with connection.cursor() as myCursor:
        myCursor.execute("SELECT question_id, question_text FROM questions ORDER BY RANDOM() LIMIT 10;")
        questions_data = myCursor.fetchall()

    questions = {}
    for q_id, q_text in questions_data:
        with connection.cursor() as myCursor:
            myCursor.execute("""
                SELECT a.answer_id, a.answer_text
                FROM answers a
                JOIN question_answers qa ON qa.answer_id = a.answer_id
                WHERE qa.question_id = %s;
            """, [q_id])
            answers = myCursor.fetchall()
        questions[q_id] = {"question_text": q_text, "answers": answers}
    return render(request, 'timeTrialApp/time_trial_start.html', {
        'questions': questions
    })


def time_trial_submit(request):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({"error": "You must be logged in to submit a Time Trial quiz."}, status=401)

        completion_time = round(float(request.POST.get("completion_time")))
        correct_answers = int(request.POST.get("correct_answers", 0))

        with connection.cursor() as myCursor:
            myCursor.execute("""
                SELECT highest_score FROM leaderboard WHERE user_id = %s
            """, [user_id])
            
            existing_time = myCursor.fetchone()

            if existing_time is None or completion_time < existing_time[0]:
                myCursor.execute("""
                    INSERT INTO leaderboard (user_id, highest_score, correct_answers)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE
                    SET highest_score = EXCLUDED.highest_score, correct_answers = EXCLUDED.correct_answers;
                """, [user_id, completion_time, correct_answers])
        return redirect("timeTrialApp:time-trial-home")