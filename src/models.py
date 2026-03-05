from pydantic import BaseModel
from typing import List, Optional


class MemoryChunk(BaseModel):
    id: str
    text: str
    source: str
    source_url: str
    date: str
    entities: List[dict]
    chunk_index: int


class Entity(BaseModel):
    name: str
    type: str  # Person, Project, Decision, Concept, Document, Event, Task
    properties: dict


class Relationship(BaseModel):
    source_entity: str
    target_entity: str
    relationship_type: str  # MENTIONED_IN, RELATED_TO, DECIDED_BY, PART_OF, ATTENDED_BY, LINKED_TO
    properties: dict