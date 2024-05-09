import os
import requests
import dotenv
from .utils import generate_embeddings
from database.client import supabase
from typing import List

notion_auth_url = os.environ.get("NOTION_AUTH_URL")
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
access_token = os.environ.get("ACCESS_TOKEN")

assert notion_auth_url, 'Must specify NOTION_AUTH_URL environment variable'

awan_key = os.environ.get("AWAN_KEY")

assert awan_key, 'Must specify AWAN_KEY environment variable'

client_id = os.environ.get('NOTION_OAUTH_CLIENT_ID')
client_secret = os.environ.get('NOTION_OAUTH_CLIENT_SECRET')

class NotionClient:
    def __init__(self):
        self.chat_id: str = None
        self.session = None
        
    def set_session(self, notion_blueprint) -> None:
        self.session = notion_blueprint.session
    
    def authorized(self, func):
        def innerFunc():
            # assert self.session.authorized, "Notion Client is unauthorized"
            func()
        return innerFunc
    
    @authorized
    def get_header(self) -> dict:
        # access_token = self.session.access_token
        
        headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'Notion-Version': '2022-06-28',
        }
        
        return headers
    
    @authorized
    def get_notes(self, resource_id: str) -> List[dict] | None:              
        headers = self.get_header()
        resp = requests.post(f'https://api.notion.com/v1/databases/{resource_id}/query', headers=headers, json={
            "sorts": [
                {
                "property": "Last edited time",
                "direction": "descending"
                }
            ],
        })
        
        data = resp.json()
        queries = data['results']
        
        all_string_values = []
        for q in queries:
            string_values = []
            for key, value in q['properties'].items():
                # Check if the value is a string
                if value['type'] in ['title', 'rich_text']:
                    # Extract the text content from the property
                    text = ''.join([item['plain_text'] for item in value[value['type']]])
                    string_values.append(text)
                    
            all_string_values.append(" ".join(string_values))
            
        embeddings = generate_embeddings(all_string_values)
        
        resp = supabase.table("notes").upsert([
            {
                "id": q['id'],
                "parent_id": q['parent']['database_id'],
                "content": content,
                "embedding": emb
            } 
            for q, emb, content in zip(queries, embeddings, all_string_values)]).execute()
        
        assert len(resp.data) > 0
        
        return resp.json(), resp.status_code
    
    @authorized
    def post_notes(self, resource_id: str, resource_name:str = "", resource_desc:str = "") -> dict | None:
        headers = self.get_header()
        data = {
            "parent" : {"database_id": resource_id},
            "properties": {
                "Name": {
                    "title": [{ "text": { "content": resource_name }}]
                },
                "Description": {
                    "rich_text": [{ "text": { "content": resource_desc }}]
                }
            }
        }
        resp = requests.post('https://api.notion.com/v1/pages', headers=headers, json=data)
        
        embeddings = generate_embeddings(resource_name + " " + resource_desc)
        
        page_content = resp.json()
        
        resp = supabase.table("notes").upsert(
            {
                "id": page_content['id'],
                "parent_id": page_content['parent']['database_id'],
                "title": resource_name,
                "content": resource_name + " " + resource_desc,
                "embedding": embeddings[0]
            } 
            ).execute()

        assert len(resp.data) > 0
        
        return resp.json(), resp.status_code
    
    @authorized
    def patch_notes(self, resource_id: str,  resource_index:int, resource_name:str = "",resource_desc:str = "") -> dict | None:
        headers = self.get_header()
        
        resp = requests.post(f'https://api.notion.com/v1/databases/{resource_id}/query', headers=headers, json={
            "sorts": [
                {
                "property": "Last edited time",
                "direction": "descending"
                }
            ],
        })
        
        data = resp.json()
        queries = data['results']
        
        assert len(queries) <= resource_index, "Index must be within query length"
        
        page_id = queries[resource_index]['id']
        
        data = {
            "parent" : {"database_id": resource_id},
            "properties": {
                "Name": {
                    "title": [{ "text": { "content": resource_name }}]
                },
                "Description": {
                    "rich_text": [{ "text": { "content": resource_desc }}]
                }
            }
        }
        
        resp = requests.patch(f'https://api.notion.com/v1/pages/{page_id}', headers=headers, json=data)
        
        embeddings = generate_embeddings(resource_name + " " + resource_desc)
        
        page_content = resp.json()
        
        resp = supabase.table("notes").upsert(
            {
                "id": page_content['id'],
                "parent_id": page_content['parent']['database_id'],
                "title": resource_name,
                "content": resource_name + " " + resource_desc,
                "embedding": embeddings[0]
            } 
            ).execute()

        assert len(resp.data) > 0
        
        return resp.json(), resp.status_code
    
    @authorized
    def delete_notes(self, resource_id: str, resource_index:int, clear_all: bool = False) -> dict | None:
        headers = self.get_header()
        resp = requests.post(f'https://api.notion.com/v1/databases/{resource_id}/query', headers=headers, json={
            "sorts": [
                {
                "property": "Last edited time",
                "direction": "descending"
                }
            ],
        })
        
        data = resp.json()
        queries = data['results']
        
        if clear_all:
            for q in queries:
                page_id = q[resource_index]['id']
            
                resp = requests.patch(f'https://api.notion.com/v1/pages/{page_id}', headers=headers, json={
                    "in_trash": True
                })
            
            resp = supabase.table("notes").delete().execute()
            
            return True
            
        else:
            assert len(queries) <= resource_index, "Index must be within query length"
            
            page_id = queries[resource_index]['id']
            
            resp = requests.patch(f'https://api.notion.com/v1/pages/{page_id}', headers=headers, json={
                "in_trash": True
            })
            
            data = supabase.table("notes").delete().eq("page_id", page_id).execute()
            
            return True
    
    @authorized
    def delete_all_notes(self) -> bool:
        return self.delete_notes(0, True)
    
    @authorized
    def query(self, resource_id: str, prompt:str) -> dict | None:
        embeddings = generate_embeddings(prompt)
        
        resp = supabase.rpc('match_documents', {
            "database_id": resource_id,
            "query_embedding": embeddings[0], 
            "match_threshold": 0.78,
            "match_count": 10,
        }).execute()
        
        prompt = f"Please answer this question, provided the question and context here, don't use your own knowledge unless specified\n\nQuestion: {prompt}\n\nContext:\n"
        for query in resp.data:
            prompt+=query['content']+"\n"
        print(prompt)
        
        headers = {
                'Authorization': f'Bearer {awan_key}',
                'Content-Type': 'application/json'
        }
        
        resp = requests.post("https://api.awanllm.com/v1/completions", headers=headers, json={
            "model": "Meta-Llama-3-8B-Instruct",
            "prompt": prompt,
        })
        
        return resp.json(), resp.status_code