from pkg.google_task_api.authorization_client import Authorization_client

if __name__ == '__main__':
    client = Authorization_client()
    print(client.get_credentials(1))