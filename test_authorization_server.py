import pkg.google_task_api.authorization_server as authorization_server
# import pkg.notion_api.authorization_server as authorization_server


if __name__ == '__main__':
    server = authorization_server.App()
    server.run(host='localhost', port=8080)