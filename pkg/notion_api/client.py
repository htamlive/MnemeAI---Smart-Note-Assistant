import os
import requests
import dotenv
from .utils import generate_embeddings
from ..database.client import supabase
from typing import List
from .authorization_client import Authorization_client
from config import config

class NotionClient:
    def __init__(self):
        self.auth_client = Authorization_client()
        self.len = None
    
    def get_header(self, chat_id: int) -> dict:
        access_token = self.auth_client.get_credentials(chat_id)
        
        assert access_token is not None, f"Empty access token, please login to Notion with {self.auth_client.get_auth_url}"
        
        headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'Notion-Version': '2022-06-28',
        }
        
        return headers
    
    def get_user(self, chat_id: int):
        headers = self.get_header(chat_id)
        resp = requests.get(f'https://api.notion.com/v1/users/me', headers=headers)
        
        data = resp.json()
        
        return data
    
    def get_database_id(self, chat_id: int):
        resp = supabase.from_("notion_database_id").select("id, database_id").eq("id", chat_id).execute()
        assert len(resp.data) > 0
        data = resp.data
        return data[0]['database_id']
    
    def get_len(self, chat_id: int):
        return len(self.get_notes(chat_id))
    
    def register_database_id(self, chat_id: int, resource_id: str):
        resp = supabase.from_("notion_database_id").upsert({
            "id": chat_id,
            "database_id": resource_id
        }).execute()
        
        assert len(resp.data) > 0
        return resp.data
        
    def register_page_database(self, chat_id: int, page_id: str, title: str):
        headers = self.get_header(chat_id)
        data = {
            "parent": { "page_id": page_id },
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": title
                    }
                }
            ],
            "properties": {
                "Name": {
                    "title": {}
                },
                "Description": {
                    "rich_text": {}
                }
            }
        }
        resp = requests.post(f'https://api.notion.com/v1/databases/', headers=headers, json=data)
        data = resp.json()
        
        resp.raise_for_status()
        resp = supabase.from_("notion_database_id").upsert({
            "id": chat_id,
            "database_id": data['id']
        }).execute()
        
        assert len(resp.data) > 0
        return resp.data
        
    def get_notes(self, chat_id: int) -> List[dict] | None:              
        headers = self.get_header(chat_id)
        resource_id = self.get_database_id(chat_id)
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
                    text = ' '.join([item['plain_text'] for item in value[value['type']]])
                    string_values.append(text)
                    
            all_string_values.append(string_values)
            
        embeddings = generate_embeddings([" ".join(strings) for strings in all_string_values])
        
        resp = supabase.table("notes").upsert([
            {
                "id": q['id'],
                "chat_id": chat_id,
                "parent_id": q['parent']['database_id'],
                "title": content[-1],
                "description": content[0],
                "embedding": emb
            } 
            for q, emb, content in zip(queries, embeddings, all_string_values)]).execute()
        
        assert len(resp.data) > 0
        
        return resp.data
    
    def get_note_content(self, chat_id, note_idx) -> str:

        # title = pagination_test_data[note_idx]["title"]
        # description = pagination_test_data[note_idx]["description"]
        
        data = self.get_notes(chat_id)
        assert note_idx < len(data)
        title = data[note_idx]["title"]
        description = data[note_idx]["description"]

        return f"<b>YOUR NOTES</b>\n\n\n<b><i>{title}</i></b>\n\n{description}"
    
    def get_data(self, resource_id:str, resource_name: str = None, resource_desc: str = None):
        if resource_name and resource_desc:
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
        elif resource_name:
            data = {
                "parent" : {"database_id": resource_id},
                "properties": {
                    "Name": {
                        "title": [{ "text": { "content": resource_name }}]
                    }
                }
            }
        elif resource_desc:
            data = {
                "parent" : {"database_id": resource_id},
                "properties": {
                    "Description": {
                        "rich_text": [{ "text": { "content": resource_desc }}]
                    }
                }
            }
        else:
            data = {
                "parent" : {"database_id": resource_id},
                "properties": {
                }
            }
        return data

    def post_notes(self, chat_id: int, resource_name:str = None, resource_desc:str = None) -> dict | None:
        headers = self.get_header(chat_id)
        resource_id = self.get_database_id(chat_id)
        
        data = self.get_data(resource_id, resource_name, resource_desc)
        
        resp = requests.post('https://api.notion.com/v1/pages', headers=headers, json=data)
        
        embeddings = generate_embeddings(resource_name + " " + resource_desc)
        
        page_content = resp.json()
        
        resp = supabase.table("notes").upsert(
            {
                "id": page_content['id'],
                "chat_id": chat_id,
                "parent_id": page_content['parent']['database_id'],
                "title": resource_name,
                "description": resource_desc,
                "embedding": embeddings[0]
            } 
            ).execute()

        assert len(resp.data) > 0
        
        return resp.data
    
    def get_notes_idx(self, chat_id: int, resource_idx: str):
        headers = self.get_header(chat_id)
        
        resp = requests.get(f'https://api.notion.com/v1/pages/{resource_idx}', headers=headers)
        
        data = resp.json()
        assert data is not None
        
        return data
    
    def patch_notes(self, chat_id:int, resource_index:int, resource_name:str = "",resource_desc:str = "") -> dict | None:
        # headers = self.get_header(chat_id)
        # resource_id = self.get_database_id(chat_id)
        
        # resp = requests.post(f'https://api.notion.com/v1/databases/{resource_id}/query', headers=headers, json={
        #     "sorts": [
        #         {
        #         "property": "Last edited time",
        #         "direction": "descending"
        #         }
        #     ],
        # })
        
        # data = resp.json()
        # queries = data['results']
        
        # assert len(queries) <= resource_index, "Index must be within query length"
        
        # page_id = queries[resource_index]['id']
                
        # data = self.get_data(resource_id, resource_name, resource_desc)
        
        # resp = requests.patch(f'https://api.notion.com/v1/pages/{page_id}', headers=headers, json=data)
        
        embeddings = generate_embeddings(resource_name + " " + resource_desc)
        
        page_content = self.get_notes_idx(chat_id, resource_index)
        
        resp = supabase.table("notes").upsert(
            {
                "id": page_content['id'],
                "chat_id": chat_id,
                "parent_id": page_content['parent']['database_id'],
                "title": resource_name,
                "description": resource_desc,
                "content": resource_name + " " + resource_desc,
                "embedding": embeddings[0]
            } 
            ).execute()

        assert len(resp.data) > 0
        
        return resp.data
    
    def delete_notes(self, chat_id:int, resource_index:str = None, clear_all: bool = False) -> dict | None:
        headers = self.get_header(chat_id)
        resource_id = self.get_database_id(chat_id)
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
                page_id = q['id']
            
                resp = requests.patch(f'https://api.notion.com/v1/pages/{page_id}', headers=headers, json={
                    "in_trash": True
                })
            
            resp = supabase.table("notes").delete().eq("database_id", resource_id).execute()
            
            return True
            
        else:            
            resp = requests.patch(f'https://api.notion.com/v1/pages/{resource_index}', headers=headers, json={
                "in_trash": True
            })
            assert resp.status_code == 200, "Page might not exist, or has_more is set to true"
            data = supabase.table("notes").delete().eq("page_id", page_id).execute()
            
            return True
    
    def delete_all_notes(self, chat_id: int) -> bool:
        return self.delete_notes(chat_id, clear_all=True)
    
    def query(self, chat_id: int, prompt:str) -> dict | None:
        resource_id = self.get_database_id(chat_id)
        embeddings = generate_embeddings(prompt)
        
        resp = supabase.rpc('match_documents', {
            "chat_id": chat_id,
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
                'Authorization': f'Bearer {config.AWAN_KEY}',
                'Content-Type': 'application/json'
        }
        
        resp = requests.post("https://api.awanllm.com/v1/completions", headers=headers, json={
            "model": "Meta-Llama-3-8B-Instruct",
            "prompt": prompt,
        })
        
        return resp.json()