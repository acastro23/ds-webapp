from django.shortcuts import render
from django.http import JsonResponse
from supabase_client import supabase



def test_supabase(request):
    # Query the 'users' table in Supabase
    response = supabase.table("users").select("*").execute()
    return JsonResponse(response.data, safe=False)