from dataclasses import asdict
from datetime import datetime
from dacite import from_dict
import google.oauth2.credentials
import googleapiclient.discovery
from pkg.google_calendar_api.model import CalendarEvent, CalendarEventList
from pkg.google_task_api.authorization_client import Authorization_client
from pkg.google_task_api.model import ListTask, Task


class GoogleCalendarApi:
    def __init__(self) -> None:
        self.authorization_client = Authorization_client()
        self.SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.events"]
        self.API_SERVICE_NAME = "calendar"
        self.API_VERSION = "v3"

    def check_auth(self, chat_id: int) -> bool:
        credentials = self.authorization_client.get_credentials(chat_id)
        return credentials is not None

    def build_service(self, chat_id: int):
        credentials = self.authorization_client.get_credentials(chat_id)
        if not credentials:
            return None

        service = googleapiclient.discovery.build(
            self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials
        )
        return service

    def get_task(self, chat_id: int, task_id: str) -> Task | None:
        service = self.build_service(chat_id)
        if service is None:
            return None

        event = service.events().get(calendarId="primary", eventId=task_id).execute()

        return _map_event_to_task(from_dict(data=event, data_class=CalendarEvent))

    def list_tasks(self, chat_id: int, page_token: str = None) -> ListTask | None:
        service = self.build_service(chat_id)
        if service is None:
            return None
        now = datetime.now().isoformat() + "Z"  # 'Z' indicates UTC time
        events = (
            service.events()
            .list(
                calendarId="primary",
                pageToken=page_token,
                timeMin=now,
                maxResults=20,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return _map_calendar_list_to_task_list(
            from_dict(data=events, data_class=CalendarEventList)
        )

    def insert_task(self, chat_id: int, task: Task) -> Task | None:
        service = self.build_service(chat_id)
        if service is None:
            return None
        event = (
            service.events()
            .insert(calendarId="primary", body=asdict(_map_task_to_event(task)))
            .execute()
        )
        return _map_event_to_task(from_dict(data=event, data_class=CalendarEvent))

    def delete_task(self, chat_id: int, task_id: str) -> None:
        service = self.build_service(chat_id)
        if service is None:
            return None
        service.events().delete(calendarId="primary", eventId=task_id).execute()

    def update_task(self, chat_id: int, task_id: str, task: Task) -> None:
        service = self.build_service(chat_id)
        if service is None:
            return None
        body = asdict(_map_task_to_event(task))
        service.events().update(
            calendarId="primary", eventId=task_id, body=body
        ).execute()


def _map_event_to_task(event: CalendarEvent) -> Task:
    return Task(
        id=event.id,
        title=event.summary,
        notes=event.description,
        due=event.end.dateTime,
    )


def _map_task_to_event(task: Task) -> CalendarEvent:
    return CalendarEvent(
        id=task.id,
        summary=task.title,
        description=task.notes,
        end={"dateTime": task.due},
    )


def _map_calendar_list_to_task_list(events: CalendarEventList) -> ListTask:
    return ListTask(
        kind=events.kind,
        etag=events.etag,
        items=[_map_event_to_task(event) for event in events.items],
        nextPageToken=events.nextPageToken,
    )
