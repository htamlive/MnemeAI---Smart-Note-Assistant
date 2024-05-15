

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Notes:
    title: Optional[str] = None
    id: Optional[str] = None
    updated: Optional[str] = None
    selfLink: Optional[str] = None
    hidden: Optional[bool] = None
    deleted: Optional[bool] = None
    parent: Optional[str] = None
    position: Optional[str] = None
    notes: Optional[str] = None
    links: List[dict] = None

@dataclass
class ListNotes:
    data: List
    startingPoint: Optional[str]
    has_more: Optional[bool]
