import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class CommandType(Enum):
    EXECUTE = 1
    STATUS = 2
    KILL = 99


class Command(BaseModel):
    identifier: uuid.UUID
    type: CommandType
    payload: Optional[str] = None
    arguments: Optional[List[str]] = None


class StatusType(Enum):
    BEACON = 1
    RECEIVED = 2
    INITIALIZED = 3
    RUNNING = 4
    FINISHED = 5
    ERROR = 6


class Message(BaseModel):
    identifier: uuid.UUID
    status: StatusType
    result: Optional[bytes] = None
