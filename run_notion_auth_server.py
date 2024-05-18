import pkg.notion_api.authorization_server as notion_authorization_server


if __name__ == '__main__':
    server = notion_authorization_server.App()
    server.run_server(host='0.0.0.0', port=5000)