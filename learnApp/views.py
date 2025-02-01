from django.shortcuts import render
from django.template.loader import render_to_string
from django.conf import settings
import os


# AC01312025 -- This method is subject to change as some algorithms will cover have long code implementations
ALGORITHMS = {
    "bubble-sort": {
        "title": "Bubble Sort",  
        "code": """def bubble_sort(arr):
    for i in range(len(arr) - 1):
        for j in range(len(arr) - i - 1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

# Sample test
arr = [4, 3, 9, 1, 2, 0, 8, 7, 10, 6, 5]
bubble_sort(arr)
print(arr)
        """,
        "step_images": []
    }
}

def algorithm_detail(request, algorithm):
    data = ALGORITHMS.get(algorithm)
    if not data:
        return render(request, 'learnApp/not_found.html')

    # AC01312025 -- All algorithms should follow this naming convention: algorithmName.html
    description_path = os.path.join(settings.BASE_DIR, "learnApp/templates/learnApp/descriptions", f"{algorithm}.html")

    if os.path.exists(description_path):
        description_html = render_to_string(f'learnApp/descriptions/{algorithm}.html')
    else:
        description_html = "<p>Description not available.</p>"
    return render(request, 'learnApp/algorithm_template.html', {'data': data, 'description': description_html})


def learn_home(request):
    """AC01312025 -- Main Learn page listing all available algorithms."""
    algorithm_list = [
        {"slug": algo, "name": algo.replace("-", " ").title()}
        for algo in ALGORITHMS.keys()
    ]
    return render(request, 'learnApp/learn_home.html', {'algorithm_list': algorithm_list})

