from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.conf import settings
from django.db import connection
import os

# Ac02112025 -- This is subject to change. Manually mapping the quiz id is not ideal
ALGORITHM_QUIZ_MAPPING = {
    "heap-sort": 1,
    "bfs": 2,
    "bubble-sort": 4,
    "selection-sort": 5,
    "merge-sort": 6,
    "quick-sort": 7,
}


def algorithm_detail(request, algorithm_name):
    """Retrieve the algorithm details from the database and load the description file."""
    with connection.cursor() as myCursor:
        myCursor.execute("SELECT display_name, code FROM algorithms WHERE name = %s", [algorithm_name])
        algorithm = myCursor.fetchone()

    if not algorithm:
        return HttpResponse("Algorithm not found", status=404)

    description_path = os.path.join(settings.BASE_DIR, "learnApp/templates/learnApp/descriptions", f"{algorithm_name}.html")
    if os.path.exists(description_path):
        with open(description_path, "r", encoding="utf-8") as file:
            description_content = file.read()
    else:
        description_content = "<p>No description available.</p>"

    quiz_id = ALGORITHM_QUIZ_MAPPING.get(algorithm_name, None)

    context = {
        "data": {
            "title": algorithm[0],  
            "code": algorithm[1],   
            "step_images": []       # Keeping empty for now
        },
        "description": description_content,
        "quiz_id": quiz_id,
    }
    return render(request, "learnApp/algorithm_template.html", context)



def learn_home(request):
    """AC01312025 -- Main Learn page listing all available algorithms from the database."""
    with connection.cursor() as myCursor:
        myCursor.execute("SELECT name, display_name FROM algorithms")
        algorithms = myCursor.fetchall()

    algorithm_list = [{"slug": algo[0], "name": algo[1]} for algo in algorithms]
    return render(request, 'learnApp/learn_home.html', {'algorithm_list': algorithm_list})