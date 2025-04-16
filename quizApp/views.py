from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.db import connection

# Create your views here.
def quiz_home(request):
    user_id = request.session.get("user_id")

    with connection.cursor() as myCursor:
        myCursor.execute("SELECT quiz_id, title FROM quizzes")
        quizzes = myCursor.fetchall()

        user_scores = {}
        completed_quizzes = set()

        if user_id:
            myCursor.execute("SELECT quiz_id, score FROM scores WHERE user_id = %s", [user_id])
            user_scores = dict(myCursor.fetchall())

            myCursor.execute("""
                SELECT quiz_id FROM user_progress 
                WHERE user_id = %s AND is_complete = TRUE
            """, [user_id])
            completed_quizzes = {row[0] for row in myCursor.fetchall()}

        quiz_list = [
            {
                "id": quiz[0],
                "name": quiz[1],
                "score": user_scores.get(quiz[0], None),
                "completed": quiz[0] in completed_quizzes
            }
            for quiz in quizzes
        ]
        return render(request, 'quizApp/quiz_home.html', {"quizzes": quiz_list})



def quiz_detail(request, quiz_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect('quizApp:quiz-home')

    stats = {
        "user_score": None,
        "user_attempts": None,
        "avg_score": None,
        "total_attempts": None,
    }

    with connection.cursor() as myCursor:
        myCursor.execute("SELECT title, description FROM quizzes WHERE quiz_id = %s;", [quiz_id])
        quiz = myCursor.fetchone()

        if not quiz:
            return render(request, 'quizApp/quiz_home.html', status=404)

        myCursor.execute("""
            SELECT score, attempts FROM scores
            WHERE user_id = %s AND quiz_id = %s;
        """, [user_id, quiz_id])
        result = myCursor.fetchone()
        if result:
            stats["user_score"], stats["user_attempts"] = result

        myCursor.execute("SELECT AVG(score), SUM(attempts) FROM scores WHERE quiz_id = %s;", [quiz_id])
        result = myCursor.fetchone()
        if result:
            stats["avg_score"], stats["total_attempts"] = result

        myCursor.execute("""
            SELECT is_complete FROM user_progress
            WHERE user_id = %s AND quiz_id = %s;
        """, [user_id, quiz_id])
        progress = myCursor.fetchone()
        show_resume = progress and not progress[0]

    return render(request, 'quizApp/quiz_detail.html', {
        'quiz': quiz,
        'quiz_id': quiz_id,
        'stats': stats,
        'show_resume': show_resume
    })
   
    

def quiz_start(request, quiz_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect('quizApp:quiz-home')

    with connection.cursor() as myCursor:
        myCursor.execute("""
            SELECT is_complete, current_question_index FROM user_progress
            WHERE user_id = %s AND quiz_id = %s
        """, [user_id, quiz_id])
        row = myCursor.fetchone()

        if row:
            is_complete, current_index = row
            if is_complete:
                current_index = 0  # this is for reeset
                myCursor.execute("""
                    UPDATE user_progress
                    SET current_question_index = 0, last_accessed = CURRENT_TIMESTAMP
                    WHERE user_id = %s AND quiz_id = %s
                """, [user_id, quiz_id])
            else:
                myCursor.execute("""
                    UPDATE user_progress
                    SET last_accessed = CURRENT_TIMESTAMP
                    WHERE user_id = %s AND quiz_id = %s
                """, [user_id, quiz_id])
        else:
            current_index = 0
            myCursor.execute("""
                INSERT INTO user_progress (user_id, quiz_id, is_complete, current_question_index)
                VALUES (%s, %s, FALSE, 0)
            """, [user_id, quiz_id])

        myCursor.execute("SELECT title FROM quizzes WHERE quiz_id = %s;", [quiz_id])
        result = myCursor.fetchone()
        quiz_title = result[0] if result else "Quiz"

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
        'quiz_title': quiz_title,
        'questions': questions,
        'resume_index': current_index
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

            myCursor.execute("""
                INSERT INTO user_progress (user_id, quiz_id, is_complete)
                VALUES (%s, %s, TRUE)
                ON CONFLICT (user_id, quiz_id) DO UPDATE
                SET is_complete = TRUE, last_accessed = CURRENT_TIMESTAMP;
            """, [user_id, quiz_id])

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