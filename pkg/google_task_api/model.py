from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Task:
    kind: Optional[str] = None
    id: Optional[str] = None
    etag: Optional[str] = None
    title: Optional[str] = None
    updated: Optional[str] = None
    selfLink: Optional[str] = None
    status: Optional[str] = None
    webViewLink: Optional[str] = None
    hidden: Optional[bool] = None
    deleted: Optional[bool] = None
    parent: Optional[str] = None
    position: Optional[str] = None
    notes: Optional[str] = None
    due: Optional[str] = None
    completed: Optional[str] = None
    links: List[dict] = None

@dataclass
class ListTask:
    kind: str
    etag: str
    items: List[Task]
    nextPageToken: Optional[str]

