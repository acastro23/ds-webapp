from django.shortcuts import render
from django.template.loader import render_to_string
from django.conf import settings
from django.db import connection
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
    },

    "heap-sort": {
        "title": "Heap Sort",  
        "code": """def Heapify(arr, n, i):
    largest = i
    l = 2 * i + 1
    r = 2 * i + 2

    if l < n and arr[i] < arr[l]:
        largest = l

    if r < n and arr[largest] < arr[r]:
        largest = r

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        Heapify(arr, n, largest)

def HeapSort(arr):
    n = len(arr)

    for i in range(n // 2, -1, -1):
        Heapify(arr, n, i)

    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        Heapify(arr, i, 0)

# Sample output
arr = [4, 3, 11, 9, 12, 10, 2, 5, 7, 6, 1, 8]
HeapSort(arr)
print("Sorted array is:", arr)
        """,
        "step_images": []
    }
}


# Ac02112025 -- This is subject to change. Manually mapping the quiz id is not ideal
ALGORITHM_QUIZ_MAPPING = {
    "heap-sort": 1,
}


def algorithm_detail(request, algorithm):
    data = ALGORITHMS.get(algorithm)
    if not data:
        return render(request, 'learnApp/not_found.html')

    description_path = os.path.join(settings.BASE_DIR, "learnApp/templates/learnApp/descriptions", f"{algorithm}.html")
    if os.path.exists(description_path):
        description_html = render_to_string(f'learnApp/descriptions/{algorithm}.html')
    else:
        description_html = "<p>Description not available.</p>"
    
    quiz_id = ALGORITHM_QUIZ_MAPPING.get(algorithm)

    return render(request, 'learnApp/algorithm_template.html', {
        'data': data,
        'description': description_html,
        'quiz_id': quiz_id, 
    })


def learn_home(request):
    """AC01312025 -- Main Learn page listing all available algorithms."""
    algorithm_list = [
        {"slug": algo, "name": algo.replace("-", " ").title()}
        for algo in ALGORITHMS.keys()
    ]
    return render(request, 'learnApp/learn_home.html', {'algorithm_list': algorithm_list})

