from ..database.setup_django_orm import setup_django_orm
setup_django_orm()

from pkg.model import Authz, ServiceType
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

import os
import json
import base64
from .utils import decode_json_base64

SCOPES = ['https://www.googleapis.com/auth/tasks']
encoded_key = os.getenv("GOOGLE_CLIENT_SECRET")
call_back_url = os.getenv("CALL_BACK_URL") # 'http://localhost:8080/oauth2callback'

class Client:
    def __init__(self):
        self.service_type = ServiceType.GOOGLE_TASK_API
        self.flow = self.create_flow()

    def create_flow(self) -> google_auth_oauthlib.flow.Flow:
        key = decode_json_base64(encoded_key)
        return google_auth_oauthlib.flow.Flow.from_client_config(key, scopes=SCOPES)

    def get_auth_url(self, chat_id: int) -> str:
        self.flow.redirect_uri = call_back_url

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