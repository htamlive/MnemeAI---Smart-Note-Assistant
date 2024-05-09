from config import config

import os
from flask import Flask, request, Response

from requests_oauthlib import OAuth2Session

from pkg.model import Authz, ServiceType

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = []
NOTION_AUTHORIZATION_URL = "https://api.notion.com/v1/oauth/authorize"
TOKEN_URL = "https://api.notion.com/v1/oauth/token"

class App:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'REPLACE ME - this value is here as a placeholder.'
        
        @self.app.route('/')
        def index():
            return 'callback'

        @self.app.route('/callback')
        def oauth2callback():
            state = request.args.get('state')

            oauth = OAuth2Session(config.NOTION_OAUTH_CLIENT_ID, state=state, redirect_uri=config.NOTION_OAUTH2_CALLBACK_URL)

            credentials = oauth.fetch_token(
                TOKEN_URL,
                client_secret=config.NOTION_OAUTH_CLIENT_SECRET,
                authorization_response=request.url,
            )

            authorization = Authz.objects.filter(current_state=state, service_type=ServiceType.NOTION.value)
            if authorization:
                authorization.update(
                    token = credentials.get("access_token")
                )
            else:
                print("Authorization not found")

            return Response('Credentials have been stored.', mimetype='text/plain')

        # self.app.register_blueprint(self.notion_blueprint)
            
    def run_server(self, host: str='localhost', port: int = 8080, debug: bool=True):
        self.app.run(host=host, port=port, debug=debug)



if __name__ == '__main__':
    app = App()
    app.run()