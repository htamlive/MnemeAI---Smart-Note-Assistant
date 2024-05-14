from config import config

from pkg.model import Authz, ServiceType
import google_auth_oauthlib.flow
import google.oauth2.credentials
import googleapiclient.discovery
from dacite import from_dict
from dataclasses import asdict

from .utils import decode_json_base64
from .authorization_client import Authorization_client
from .model import ListTask, Task

from config import MAX_RESULTS


class GoogleTaskClient:
    def __init__(self):
        self.authorization_client = Authorization_client()
        self.SCOPES = ['https://www.googleapis.com/auth/tasks']
        self.API_SERVICE_NAME = 'tasks'
        self.API_VERSION = 'v1'

    def check_auth(self, chat_id: int) -> bool:
        credentials = self.authorization_client.get_credentials(chat_id)
        return credentials is not None


    def build_service(self, chat_id: int):
        credentials = self.authorization_client.get_credentials(chat_id)
        if not credentials:
            return None
        
        service = googleapiclient.discovery.build(self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials)
        return service
    
    def list_tasks(
            self, 
            chat_id: int, 
            completed_max: str = None, 
            completed_min: str = None, 
            due_max: str = None,
            due_min: str = None,
            max_results: int = MAX_RESULTS,
            page_token: str = None,
            show_completed: bool = None,
            show_deleted: bool = None,
            show_hidden: bool = None,
            updated_min: str = None
        ) -> ListTask | None:
        service = self.build_service(chat_id)
        if not service:
            return None
        
        results = service.tasks().list(
            tasklist='@default', 
            completedMax=completed_max, 
            completedMin=completed_min, 
            dueMax=due_max, dueMin=due_min, 
            maxResults=max_results, 
            pageToken=page_token, 
            showCompleted=show_completed, 
            showDeleted=show_deleted, 
            showHidden=show_hidden, 
            updatedMin=updated_min
        ).execute()

        return from_dict(data_class=ListTask, data=results)
    
    def get_task(self, chat_id: int, task_id: str) -> Task | None:
        service = self.build_service(chat_id)
        if not service:
            return None
        
        result = service.tasks().get(tasklist='@default', task=task_id).execute()
        return from_dict(data_class=Task, data=result)
    
    def update_task(self, chat_id: int, task_id: str, task: Task) -> Task | None:

        service = self.build_service(chat_id)
        if not service:
            return None

        result = service.tasks().update(tasklist='@default', task=task_id, body=asdict(task)).execute()
        return from_dict(data_class=Task, data=result)
    
    def insert_task(self, chat_id: int, task: Task) -> Task | None:
        service = self.build_service(chat_id)
        if not service:
            return None
        
        result = service.tasks().insert(tasklist='@default', body=asdict(task)).execute()
        return from_dict(data_class=Task, data=result)

    def delete_task(self, chat_id: int, task_id: str) -> None:
        service = self.build_service(chat_id)
        if not service:
            return None
        
        service.tasks().delete(tasklist='@default', task=task_id).execute()