from dataclasses import asdict
from datetime import datetime, timedelta
from dacite import from_dict
import google.oauth2.credentials
import googleapiclient.discovery
import pytz
from pkg.google_calendar_api.model import CalendarEvent, CalendarEventList
from pkg.google_task_api.authorization_client import Authorization_client
from pkg.google_task_api.model import ListTask, Task


class GoogleCalendarApi:
    def __init__(self) -> None:
        self.authorization_client = Authorization_client()
        self.SCOPES = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events",
        ]
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

    def list_tasks(
        self, chat_id: int, timezone: str, page_token: str = None
    ) -> ListTask | None:
        service = self.build_service(chat_id)
        if service is None:
            return None
        tz = pytz.timezone(timezone)
        now = datetime.now(tz).isoformat()
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
        print (events)
        return _map_calendar_list_to_task_list(
            from_dict(data=events, data_class=CalendarEventList)
        )

    def insert_task(self, chat_id: int, task: Task) -> Task | None:
        service = self.build_service(chat_id)
        if service is None:
            return None
        event = _map_task_to_event(task)
        timezone = "Etc/GMT" + task.timezone[7:]
        tz = pytz.timezone(timezone)

        due_datetime = datetime.strptime(task.due, "%Y-%m-%d %H:%M")
        due_datetime = tz.localize(due_datetime)
        event.end.dateTime = (due_datetime + timedelta(hours=2)).isoformat()
        # event.end.dateTime = event.end.dateTime.replace("Z", f"+{timezone}:00")

        e = self.encapsulate(
            event,
            timezone,
            due_datetime.isoformat(),
        )
        event = service.events().insert(calendarId="primary", body=e).execute()
        print("Event created: %s" % (event.get("htmlLink")))
        return _map_event_to_task(from_dict(data=event, data_class=CalendarEvent))

    def encapsulate(self, event, timezone, start):
        return {
            "summary": event.summary,
            "description": event.description,
            "start": {
                "dateTime": start,
                "timeZone": timezone,
            },
            "end": {
                "dateTime": event.end.dateTime,
                "timeZone": timezone,
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},
                    {"method": "popup", "minutes": 10},
                ],
            },
        }

    def delete_task(self, chat_id: int, task_id: str) -> None:
        service = self.build_service(chat_id)
        if service is None:
            return None
        service.events().delete(calendarId="primary", eventId=task_id).execute()

    def update_task(self, chat_id: int, task_id: str, task: Task) -> None:
        service = self.build_service(chat_id)
        if service is None:
            return None
        body = self.encapsulate(
            _map_task_to_event(task),
            task.timezone,
            task.start,
        )
        service.events().update(
            calendarId="primary", eventId=task_id, body=body
        ).execute()


def _map_event_to_task(event: CalendarEvent) -> Task:
    return Task(
        id=event.id,
        title=event.summary,
        notes=event.description,
        due=event.end.dateTime,
        timezone=event.end.timeZone,
        start=event.start.dateTime,
    )


def _map_task_to_event(task: Task) -> CalendarEvent:
    return CalendarEvent(
        id=task.id,
        summary=task.title,
        description=task.notes,
        start=CalendarEvent.DateTime(
            dateTime=task.start,
            timeZone=task.timezone,
        ),
        end=CalendarEvent.DateTime(
            dateTime=task.due,
            timeZone=task.timezone,
        ),
    )


def _map_calendar_list_to_task_list(events: CalendarEventList) -> ListTask:
    return ListTask(
        kind=events.kind,
        etag=events.etag,
        items=[_map_event_to_task(event) for event in events.items],
        nextPageToken=events.nextPageToken,
    )
