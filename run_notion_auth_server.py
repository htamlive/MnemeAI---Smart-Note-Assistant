import pkg.notion_api.authorization_server as notion_authorization_server


if __name__ == '__main__':
    server = notion_authorization_server.App()
    server.run_server(host='localhost', port=5000)