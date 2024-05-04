import sys
import os

sys.path.append(".")

from dotenv import load_dotenv
load_dotenv()

import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from utils import decode_json_base64
from pkg.database.setup_django_orm import setup_django_orm
setup_django_orm()

from pkg.model import Authz, ServiceType

os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

encoded_key = os.getenv("GOOGLE_CLIENT_SECRET")
app_credential = decode_json_base64(encoded_key)

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/tasks']
API_SERVICE_NAME = 'tasks'
API_VERSION = 'v1'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'REPLACE ME - this value is here as a placeholder.'


@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/oauth2callback')
def oauth2callback():
    state = flask.request.args.get('state')

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
      app_credential, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    print("authorization_response: ", authorization_response)

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



if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)