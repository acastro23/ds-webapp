from django.shortcuts import render
from django.db import connection


# Create your views here.

def leaderboard_main(request):
    with connection.cursor() as myCursor:
        myCursor.execute("""
            SELECT u.username, l.correct_answers
            FROM leaderboard l
            JOIN users u ON l.user_id = u.user_id
            ORDER BY l.correct_answers DESC
            LIMIT 5;
        """)
        top_users = myCursor.fetchall()
    return render(request, "leaderboardApp/leaderboard.html", {"top_users": top_users})