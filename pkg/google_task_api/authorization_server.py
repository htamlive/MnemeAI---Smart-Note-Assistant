from config import config

import os

import flask
import google_auth_oauthlib.flow

from .utils import decode_json_base64

from pkg.model import Authz

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

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

            authorization = Authz.objects.get(current_state=state)
            if authorization:
                authorization.token = credentials.token
                authorization.refresh_token = credentials.refresh_token
                authorization.client_id = credentials.client_id
                authorization.client_secret = credentials.client_secret
                authorization.save()
            else:
                print("Authorization not found")

            return flask.Response('Credentials have been stored.', mimetype='text/plain')
    
    def run(self, host: str='localhost', port: int=8080, debug: bool=True):
        self.app.run(host=host, port=port, debug=debug)



if __name__ == '__main__':
    app = App()
    app.run()