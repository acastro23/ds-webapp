from supabase_client import supabase
from django.middleware.csrf import get_token
import json
import bcrypt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
import logging

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

        # validating the data from the JSON body
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
        
        # If there are any validation errors at all then return this message back to the user when they attempt to create the account
        if val_errors:
            return JsonResponse({"error": val_errors}, status=400)
        
        try:
            existing_user = supabase.table("users").select("*").eq("email", email).execute()
            if existing_user.data:
                return JsonResponse({"error": "User with this email already exist!"}, status=400)
            
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            myResponse = supabase.table("users").insert({
                "username": username,
                "email": email,
                "password": hashed_password.decode("utf-8"),
            }).execute()
            return JsonResponse(myResponse.data, safe=False)
        
        except Exception as e:
            myLogger.error(f"An error occurred during registration due to: {e}", exc_info=True)
            return JsonResponse({"error": "An unexpected error has occurred. Please try again later."}, status=500)
    return JsonResponse({"error": "Invalid request method is being used"}, status=405)


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
            data = json.loads(request.body)
        except json.JSONDecodeError:
            myLogger.error("Invalid JSON data received during login attempt")
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        
        email = data.get("email")
        password = data.get("password")

        if not email:
            return JsonResponse({"error": "An email is required for login"}, status=400)
        if not password:
            return JsonResponse({"error": "Password is required for login"}, status=400)
        
        try:
            user_response = supabase.table("users").select("*").eq("email", email).execute()
            if not user_response:
                return JsonResponse({"error": "Invalid email or password"}, status=401)
            myUser = user_response.data[0]

            stored_password = myUser["password"]

            if not bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
                return JsonResponse({"error": "Invalid email or password"}, status=401)
            
            #--------------  AC0122 -- Test code for storing the users info in session  ---------------
            request.session["user_id"] = myUser["user_id"]
            request.session["username"] = myUser["username"]
            #------------------------------------------------------------------------------------------ 

            return JsonResponse({"message": "Login was successful", "username": myUser["username"]}, status=200)

        except Exception as e:
            myLogger.error(f"Error during login: {e}", exc_info=True)
            return JsonResponse({"error": "An unexpected error has occurred. Please try again later."}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)


def logout_user(request):
    """ Logging out should be simple, and clears the session """
    if request.method == "POST":
        request.session.flush()
        return JsonResponse({"message": "You have logged out"}, status=200)
    return JsonResponse({"error": "Invalid request method"}, status=405)
            


def test_supabase(request):
    # Query the 'users' table in Supabase
    response = supabase.table("users").select("*").execute()
    return JsonResponse(response.data, safe=False)