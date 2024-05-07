import os
import requests
import dotenv
from supabase import create_client, Client
from transformers import AutoTokenizer, AutoModel
from utils import average_pool
from torch import no_grad
from database.client import supabase
from flask import Flask, redirect, url_for, request, jsonify
from typing import List
from flask_dance.consumer import OAuth2ConsumerBlueprint

notion_auth_url = os.environ.get("NOTION_AUTH_URL")
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# access_token = os.environ.get("ACCESS_TOKEN")

assert notion_auth_url, 'Must specify NOTION_AUTH_URL environment variable'

awan_key = os.environ.get("AWAN_KEY")

assert awan_key, 'Must specify AWAN_KEY environment variable'

client_id = os.environ.get('NOTION_OAUTH_CLIENT_ID')
client_secret = os.environ.get('NOTION_OAUTH_CLIENT_SECRET')

class NotionClient:
    def __init__(self):
        self.notion_blueprint = OAuth2ConsumerBlueprint(
            "login_notion",
            __name__,
            client_id=client_id,
            client_secret=client_secret,
            base_url="https://api.notion.com",
            token_url="https://api.notion.com/v1/oauth/token",
            authorization_url="https://api.notion.com/v1/oauth/authorize",
        )
        self.authorized : bool = False
        self.access_token : str = None
        self.chat_id: str = None
    
    def get_notes(self) -> List[dict] | None:
        assert self.notion_blueprint.session.authorized
            
        
    
    def post_notes(self, name:str, desc:str = "") -> dict | None:
        pass
    
    def patch_notes(self, name:str, index:int, desc:str = "") -> dict | None:
        pass
    
    def delete_notes(self, index:int) -> dict | None:
        pass
    
    def delete_all_notes(self):
        pass
    
    def query(self, prompt:str) -> dict | None:
        pass