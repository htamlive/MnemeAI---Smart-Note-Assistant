from pkg.google_task_api.api_client import Client

client = Client()

print(client.get_auth_url(3))