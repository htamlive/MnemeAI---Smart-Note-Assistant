from config import config

from pkg.model import Authz, ServiceType
import google_auth_oauthlib.flow
import google.oauth2.credentials
from .utils import decode_json_base64

SCOPES = ['https://www.googleapis.com/auth/tasks']

class Authorization_client:
    def __init__(self):
        self.service_type = ServiceType.GOOGLE_TASK_API
        self.flow = self.create_flow()

    def create_flow(self) -> google_auth_oauthlib.flow.Flow:
        key = decode_json_base64(config.GOOGLE_APP_CREDENTIAL)
        return google_auth_oauthlib.flow.Flow.from_client_config(key, scopes=SCOPES)

    def get_auth_url(self, chat_id: int) -> str:
        self.flow.redirect_uri = config.GOOGLE_OAUTH2_CALLBACK_URL

        authorization_url, state = self.flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent')

        # Store the state so the callback can verify the auth server response.
        Authz.objects.update_or_create(
            chat_id=chat_id,
            service_type=self.service_type.value,
            defaults={'current_state': state}
        )

        return authorization_url

    def get_credentials(self, chat_id: int) -> google.oauth2.credentials.Credentials | None:
        authz = Authz.objects.get(chat_id=chat_id, service_type=self.service_type.value)
        if authz:
            return google.oauth2.credentials.Credentials(
                token=authz.token,
                refresh_token=authz.refresh_token,
                client_id=authz.client_id,
                client_secret=authz.client_secret,
                token_uri=self.flow.client_config['token_uri'],
                scopes=SCOPES
            )
        return None