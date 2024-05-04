from dotenv import load_dotenv
load_dotenv()

from pkg.google_task_api.client import Client

client = Client()

print(client.get_auth_url(2))