from supabase import create_client

# Your same credentials
supabase_url = "https://uhbzldqdbhdyfuxwkqcn.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVoYnpsZHFkYmhkeWZ1eHdrcWNuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MjE1MDkxNSwiZXhwIjoyMDU3NzI2OTE1fQ.JauAr1A-gaxwNLau9agXY7boGAm01kHJHDTfF-YMDSM"

# Initialize the client
supabase = create_client(supabase_url, supabase_key)