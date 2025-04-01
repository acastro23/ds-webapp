from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse

# Create your views here.
def time_trial_home(request):
    return render(request, 'timeTrialApp/time_trial_home.html')


def time_trial_start(request):
    """AC02152025:
            All questions from the questions table along with their answer choices will be queried and selected at random for this mode.
        Ideally, it'll keep showing users a new question until the timer runs out OR if the user manages to answer every single question in the database.
    """
    with connection.cursor() as myCursor:
        myCursor.execute("""
            SELECT q.question_id, q.question_text, a.answer_id, a.answer_text, a.is_correct
            FROM questions q
            JOIN question_answers qa ON qa.question_id = q.question_id
            JOIN answers a ON qa.answer_id = a.answer_id
            ORDER BY RANDOM();
        """)
        question_data = myCursor.fetchall()

    questions = {}
    for question_id, question_text, answer_id, answer_text, is_correct in question_data:
        if question_id not in questions:
            questions[question_id] = {
                "question_text": question_text,
                "answers": []
            }
        questions[question_id]["answers"].append((answer_id, answer_text, is_correct))
    return render(request, 'timeTrialApp/time_trial_start.html', {"questions": questions})


def time_trial_submit(request):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({"error": "You must be logged in to submit a Time Trial quiz."}, status=401)

        try:
            completion_time = round(float(request.POST.get("completion_time", "0")))
        except ValueError:
            return JsonResponse({"error": "Invalid or missing completion time."}, status=400)

        try:
            correct_answers = int(request.POST.get("correct_answers", "0"))
        except ValueError:
            return JsonResponse({"error": "Invalid or missing correct answers count."}, status=400)

        with connection.cursor() as myCursor:
            myCursor.execute("""
                SELECT highest_score, correct_answers FROM leaderboard WHERE user_id = %s
            """, [user_id])

            existing_entry = myCursor.fetchone()

            if (
                existing_entry is None or
                correct_answers > existing_entry[1] or
                (correct_answers == existing_entry[1] and completion_time < existing_entry[0])
            ):
                myCursor.execute("""
                    INSERT INTO leaderboard (user_id, highest_score, correct_answers)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE
                    SET highest_score = EXCLUDED.highest_score, correct_answers = EXCLUDED.correct_answers;
                """, [user_id, completion_time, correct_answers])
        return redirect("timeTrialApp:time-trial-home")
