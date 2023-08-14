import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, validator


class CommandType(Enum):
    RUN = 1
    KILL = 99


class Command(BaseModel):
    identifier: Optional[uuid.UUID] = None
    type: CommandType
    payload: Optional[str] = None
    arguments: Optional[List[str]] = None

    @validator("identifier", pre=True, always=True)
    def generate_identifier_uuid(cls, value):
        if not value:
            return uuid.uuid4()
        return value


class StatusType(Enum):
    BEACON = 1
    RECEIVED = 2
    INITIALIZED = 3
    RUNNING = 4
    FINISHED = 5
    ERROR = 6


class Message(BaseModel):
    identifier: Optional[uuid.UUID] = None
    status: StatusType
    result: Optional[bytes] = None

    @validator("identifier", pre=True, always=True)
    def generate_identifier_uuid(cls, value):
        if not value:
            return uuid.uuid4()
        return value
