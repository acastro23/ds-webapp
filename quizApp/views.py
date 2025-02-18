from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.db import connection

# Create your views here.
def quiz_home(request):
    """AC02072025:
            This method is for the home page of our quiz app. So, like with the 'learn-home' page, this should display a list of all the quizzes our application offers,
            What the user should see from this list is the title of the quiz which is pulled from the database.
    """
    with connection.cursor() as myCursor:
        myCursor.execute("SELECT quiz_id, title FROM quizzes")
        quizzes = myCursor.fetchall()
    return render(request, 'quizApp/quiz_home.html', {'quizzes': quizzes})


def quiz_detail(request, quiz_id):
    """AC02072025:
            The 'quiz_detail' method fetches the content of the quiz from the database and renders it to the 'quiz_detail.html' page
    """
    with connection.cursor() as myCursor:
        myCursor.execute("SELECT title, description FROM quizzes WHERE quiz_id = %s;", [quiz_id])
        quiz = myCursor.fetchone()
    
    if quiz:
        return render(request, 'quizApp/quiz_detail.html', {'quiz': quiz, 'quiz_id': quiz_id})      # this page is just a preview page, not the actual quiz page where the user answers questions
    else:
        return render(request, 'quizApp/quiz_not_found.html', status=404)
    

def quiz_start(request, quiz_id):
    with connection.cursor() as myCursor:
        myCursor.execute("SELECT question_id, question_text FROM questions WHERE quiz_id = %s;", [quiz_id])
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
    return render(request, 'quizApp/quiz_start.html', {
        'quiz_id': quiz_id,
        'quiz_title': f"Quiz {quiz_id}",
        'questions': questions
    })


def next_question(request, quiz_id):
    if request.method == 'POST':
        request.session['current_question_index'] = request.session.get('current_question_index', 0) + 1
    return redirect('quizApp:quiz-start', quiz_id=quiz_id)


def prev_question(request, quiz_id):
    if request.method == 'POST':
        request.session['current_question_index'] = max(0, request.session.get('current_question_index', 0) - 1)
    return redirect('quizApp:quiz-start', quiz_id=quiz_id)


def quiz_submit(request, quiz_id):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({"error": "You must be logged in to submit a quiz."}, status=401)

        user_answers = {}
        for key, value in request.POST.items():
            if key.startswith("question_"):
                question_id = key.split("_")[1]
                user_answers[int(question_id)] = int(value)
        
        with connection.cursor() as myCursor:
            myCursor.execute("""
                SELECT q.question_id, a.answer_id
                FROM questions q
                JOIN question_answers qa ON qa.question_id = q.question_id
                JOIN answers a ON qa.answer_id = a.answer_id
                WHERE q.quiz_id = %s AND a.is_correct = TRUE;
            """, [quiz_id])
            correct_answers = {row[0]: row[1] for row in myCursor.fetchall()}

        score = sum(1 for q_id, a_id in user_answers.items() if correct_answers.get(q_id) == a_id)

        with connection.cursor() as myCursor:
            myCursor.execute("""
                INSERT INTO scores (user_id, quiz_id, score, attempts)
                VALUES (%s, %s, %s, 1)
                ON CONFLICT (user_id, quiz_id) DO UPDATE
                SET score = EXCLUDED.score, attempts = scores.attempts + 1;
            """, [user_id, quiz_id, score])

        return redirect('quizApp:quiz-results', quiz_id=quiz_id, score=score)

    return redirect('quizApp:quiz-home')


def quiz_results(request, quiz_id, score):
    """Displays the quiz results page."""
    with connection.cursor() as myCursor:
        myCursor.execute("SELECT title FROM quizzes WHERE quiz_id = %s;", [quiz_id])
        quiz = myCursor.fetchone()

        myCursor.execute("SELECT COUNT(*) FROM questions WHERE quiz_id = %s;", [quiz_id])
        total_questions = myCursor.fetchone()[0]

    quiz_title = quiz[0] if quiz else "Unknown Quiz"
    score_percentage = (int(score) / total_questions) * 100 if total_questions > 0 else 0
    score_percentage = f"{int(score_percentage)}%"

    return render(request, 'quizApp/quiz_results.html', {
        'quiz_id': quiz_id,
        'quiz_title': quiz_title,
        'score': score,
        'score_percentage': score_percentage
    })