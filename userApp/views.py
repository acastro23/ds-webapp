from supabase_client import supabase
from django.middleware.csrf import get_token
import json
import bcrypt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
import re
import logging
import base64

myLogger = logging.getLogger(__name__)

# AC01282025 -- The following three functions will be helpers for validation personal information such as: username, email, and password, hence why request is not an argument here
def val_user(username):
    """
    The username must be at least 3 characters long and can only contain letters, numbers, and underscores(will be checked by using regex expresssions)
    """
    if not username or len(username) < 3:
        return "Username must be at least 3 characters long"
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return "Username can only contain letters, numbers, and underscores"
    return None


def val_email(email):
    """email should just follow standard email format like: alexscastro2002@gmail.com """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email or not re.match(email_regex, email):
        return "Invalid email format"
    return None


def val_password(password):
    """ A password should contain at least 8 characters, at least one uppercase letter, and at least one digit to register """
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one digit"
    if not any(char.isupper() for char in password):
        return "Password must contain at least one uppercase letter"
    return None


@csrf_exempt
def register_user(request):
    """
    The breakdown:
    -------------
        * check to make sure that is sent back is valid and ensure right method is used.
        * check database for matching emails and preventing registration using dup. email address
        * register the user to the database and account for unexpected errors
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            myLogger.error("Invalid JSON data received")
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        val_errors = []
        username_error = val_user(username)
        if username_error:
            val_errors.append(username_error)
        email_error = val_email(email)
        if email_error:
            val_errors.append(email_error)
        password_error = val_password(password)
        if password_error:
            val_errors.append(password_error)
        
        if val_errors:
            return JsonResponse({"error": val_errors}, status=400)

        try:
            existing_user = supabase.table("users").select("user_id").eq("email", email).execute()
            if existing_user.data and len(existing_user.data) > 0:
                return JsonResponse({"error": "User with this email already exists!"}, status=400)

            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            myResponse = supabase.table("users").insert({
                "username": username,
                "email": email,
                "password": hashed_password,
            }).execute()
            
            return JsonResponse(myResponse.data, safe=False)

        except Exception as e:
            myLogger.error(f"An error occurred during registration due to: {e}", exc_info=True)
            return JsonResponse({"error": "An unexpected error has occurred. Please try again later."}, status=500)
    return JsonResponse({"error": "Invalid request method is being used"}, status=405)



@csrf_exempt
def login_user(request):
    """
    The breakdown:
    -------------
        * check to make sure that is sent back is valid and ensure right method is used.
        * ensure there is an email and password input for login
        * ensure there is a match for the input in the database
        * if there is a match, start a session(cookie)
        * account for unexpected errors as e
    """
    if request.method == "POST":
        try:
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = request.POST

            email = data.get("email")
            password = data.get("password")

            if not email:
                return JsonResponse({"error": "An email is required for login"}, status=400)
            if not password:
                return JsonResponse({"error": "Password is required for login"}, status=400)

            user_response = supabase.table("users").select("*").eq("email", email).execute()
            if not user_response.data:
                return JsonResponse({"error": "Invalid email or password"}, status=401)
            
            myUser = user_response.data[0]

            stored_password = myUser.get("password", "").encode("utf-8")
            if not bcrypt.checkpw(password.encode("utf-8"), stored_password):
                return JsonResponse({"error": "Invalid email or password"}, status=401)

            #--------------  AC0122 -- Test code for storing the users info in session  ---------------
            request.session["user_id"] = myUser["user_id"]
            request.session["username"] = myUser["username"]
            #------------------------------------------------------------------------------------------

            return JsonResponse({"message": "Login was successful", "username": myUser["username"]}, status=200)

        except Exception as e:
            myLogger.error(f"Error during login: {e}", exc_info=True)
            return JsonResponse({"error": "An unexpected error occurred. Please try again."}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)



@csrf_exempt
def update_email(request):
    """
    In regards to profile updates, only the email can be updated as of right now. 
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            myLogger.error("Invalid JSON data received")
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
    
        user_id = request.session.get("user_id")
        if not user_id:
            return JsonResponse({"error": "Authentication required"}, status=401)
        new_email = data.get("email")

        email_val = val_email(new_email)
        if email_val:
            return JsonResponse({"error": email_val}, status=400)
        
        try:
            existing_user = supabase.table("users").select("user_id").eq("email", new_email).execute()
            if existing_user.data:
                return JsonResponse({"error": "This email is already being used"}, status=400)
            update_response = supabase.table("users").update({"email": new_email}).eq("user_id", user_id).execute()

            if update_response.data:
                return JsonResponse({"message": "Email has been updated"}, status=200)
            else:
                return JsonResponse({"error": "Failed to update email"}, status=500)
            
        except Exception as e:
            myLogger.error(f"Error updating email due to: {e}", exc_info=True)
            return JsonResponse({"error": "An unexpected error occurred. Please try again"}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=500)


@csrf_exempt
def logout_user(request):
    if request.method == "POST":
        request.session.pop("user_id", None)
        request.session.pop("username", None)
        return redirect("home")
    return JsonResponse({"error": "Invalid request method"}, status=405)


def profile_page(request):
    return render(request, "userApp/profile.html")


@csrf_exempt
def profile_data(request):
    user_id = request.session.get("user_id")
    username = request.session.get("username")

    if not user_id:
        return JsonResponse({"error": "User not logged in"}, status=401)

    if request.method == "GET":
        try:
            user_result = supabase.table("users").select("bio, profile_picture").eq("user_id", user_id).execute()
            if not user_result.data:
                return JsonResponse({"error": "User not found"}, status=404)
            user_data = user_result.data[0]

            score_data = supabase.table("scores")\
                .select("quiz_id, score")\
                .eq("user_id", user_id)\
                .execute()

            quizzes_completed = len({entry["quiz_id"] for entry in score_data.data})
            highest_score = max((entry["score"] for entry in score_data.data), default=0)

            leaderboard_data = supabase.table("leaderboard")\
                .select("user_id, correct_answers")\
                .order("correct_answers", desc=True)\
                .execute()

            user_rank = None
            time_trial_best = None
            for idx, entry in enumerate(leaderboard_data.data):
                if entry["user_id"] == user_id:
                    user_rank = idx + 1
                    time_trial_best = entry["correct_answers"]
                    break

            return JsonResponse({
                "bio": user_data.get("bio"),
                "profile_picture": user_data.get("profile_picture"),
                "username": username,
                "quiz_count": quizzes_completed,
                "highest_score": highest_score,
                "rank": user_rank,
                "time_trial": time_trial_best
            })

        except Exception as e:
            myLogger.error("Error fetching profile data", exc_info=True)
            return JsonResponse({"error": "An unexpected error occurred"}, status=500)

    elif request.method == "POST":
        try:
            if request.content_type.startswith("multipart/form-data"):
                bio = request.POST.get("bio", "")
                image_file = request.FILES.get("profile_picture")
                base64_image = None

                if image_file:
                    base64_image = "data:" + image_file.content_type + ";base64," + base64.b64encode(image_file.read()).decode("utf-8")

                update_data = {}
                if bio:
                    update_data["bio"] = bio
                if base64_image:
                    update_data["profile_picture"] = base64_image

                supabase.table("users").update(update_data).eq("user_id", user_id).execute()
                return JsonResponse({"message": "Profile updated"})

            else:
                data = json.loads(request.body)

                if "quiz_id" in data and "current_question_index" in data:
                    supabase.table("user_progress").update({
                        "current_question_index": data["current_question_index"]
                    }).eq("user_id", user_id).eq("quiz_id", data["quiz_id"]).execute()
                    return JsonResponse({"message": "Progress saved"})

                update_data = {}
                if "bio" in data:
                    update_data["bio"] = data["bio"]
                if data.get("remove_picture", False):
                    update_data["profile_picture"] = None

                if update_data:
                    supabase.table("users").update(update_data).eq("user_id", user_id).execute()

                return JsonResponse({"message": "Profile updated"})
        except Exception as e:
            myLogger.error("Error updating profile", exc_info=True)
            return JsonResponse({"error": "An unexpected error occurred"}, status=500)