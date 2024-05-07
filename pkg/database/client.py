from supabase import create_client, Client
import os

supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')

assert supabase_url, 'Must specify SUPABASE_URL environment variable'
assert supabase_key, 'Must specify SUPABASE_KEY environment variable'

supabase: Client = create_client(supabase_url, supabase_key)