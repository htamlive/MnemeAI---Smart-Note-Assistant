import pkg.google_task_api.authorization_server as google_task_authorization_server


if __name__ == '__main__':
    server = google_task_authorization_server.App()
    server.run(host='0.0.0.0', port=8080, debug=False)