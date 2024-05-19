from config import config

from pkg.model import Authz, ServiceType
from requests_oauthlib import OAuth2Session

SCOPES = []
NOTION_AUTHORIZATION_URL = "https://api.notion.com/v1/oauth/authorize"

class Authorization_client:
    def __init__(self):
        self.service_type = ServiceType.NOTION
        self.flow = self.create_flow()

    def create_flow(self) -> OAuth2Session:
        return OAuth2Session(
            client_id=config.NOTION_OAUTH_CLIENT_ID,
            redirect_uri=config.NOTION_OAUTH2_CALLBACK_URL,
            scope=SCOPES
        )

    def get_auth_url(self, chat_id: int) -> str:
        authorization_url, state = self.flow.authorization_url(NOTION_AUTHORIZATION_URL)

        # Store the state so the callback can verify the auth server response.
        Authz.objects.update_or_create(
            chat_id=chat_id,
            service_type=self.service_type.value,
            defaults={'current_state': state}
        )

        return authorization_url

    # load the credentials from the database
    def get_credentials(self, chat_id: int) -> str | None:
        try:
            authorization = Authz.objects.get(chat_id=chat_id, service_type=self.service_type.value)
            return authorization.token
        except Authz.DoesNotExist:
            return None