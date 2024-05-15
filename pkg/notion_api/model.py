

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Note:
    title: Optional[str]
    id: Optional[str]
    updated: Optional[str]
    selfLink: Optional[str]
    hidden: Optional[bool]
    deleted: Optional[bool]
    parent: Optional[str]
    position: Optional[str]
    notes: Optional[str]
    links: List[dict]

@dataclass
class ListNotes:
    items: List[Note]
    startingPoint: Optional[int]