from supabase import create_client
from decouple import config

supabase_url = config("SUPABASE_URL")
supabase_key = config("SUPABASE_API_KEY")

supabase = create_client(supabase_url, supabase_key)