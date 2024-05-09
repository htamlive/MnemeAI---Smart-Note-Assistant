from config import config

import os

import flask
import google_auth_oauthlib.flow

from .utils import decode_json_base64

from pkg.model import Authz, ServiceType

# from ..notion_api.client import NotionClient
# from flask_dance.consumer import OAuth2ConsumerBlueprint

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

client_id = os.environ.get('NOTION_OAUTH_CLIENT_ID')
client_secret = os.environ.get('NOTION_OAUTH_CLIENT_SECRET')

encoded_key = config.GOOGLE_APP_CREDENTIAL
app_credential = decode_json_base64(encoded_key)

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/tasks']
API_SERVICE_NAME = 'tasks'
API_VERSION = 'v1'

class App:
    def __init__(self):
        self.app = flask.Flask(__name__)
        self.app.secret_key = 'REPLACE ME - this value is here as a placeholder.'
        # self.notion_blueprint = OAuth2ConsumerBlueprint(
        #     "login_notion",
        #     __name__,
        #     client_id=client_id,
        #     client_secret=client_secret,
        #     base_url="https://api.notion.com",
        #     token_url="https://api.notion.com/v1/oauth/token",
        #     authorization_url="https://api.notion.com/v1/oauth/authorize",
        # )
        
        @self.app.route('/')
        def index():
            return 'oauth2callback'

        @self.app.route('/oauth2callback')
        def oauth2callback():
            state = flask.request.args.get('state')

            flow = google_auth_oauthlib.flow.Flow.from_client_config(
            app_credential, scopes=SCOPES, state=state)
            flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

            # Use the authorization server's response to fetch the OAuth 2.0 tokens.
            authorization_response = flask.request.url

            flow.fetch_token(authorization_response=authorization_response)

            # Store credentials
            credentials = flow.credentials

            authorization = Authz.objects.filter(current_state=state, service_type=ServiceType.GOOGLE_TASK_API.value)
            if authorization:
                authorization.update(
                    service_type=ServiceType.GOOGLE_TASK_API.value,
                    token=credentials.token,
                    refresh_token=credentials.refresh_token,
                    client_id=credentials.client_id,
                    client_secret=credentials.client_secret,
                )
            else:
                print("Authorization not found")

            return flask.Response('Credentials have been stored.', mimetype='text/plain')

        # self.app.register_blueprint(self.notion_blueprint)
            
    def run(self, host: str='localhost', port: int=8080, debug: bool=True):
        self.app.run(host=host, port=port, debug=debug)



if __name__ == '__main__':
    app = App()
    app.run()