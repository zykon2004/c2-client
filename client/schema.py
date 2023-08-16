import base64
import hashlib
import hmac
import json
import secrets
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, validator
from settings import SECRET_KEY


class CommandType(Enum):
    RUN = 1
    KILL = 99


class BaseMessage(BaseModel):
    identifier: Optional[uuid.UUID] = None

    @validator("identifier", pre=True, always=True)
    def generate_identifier_uuid(cls, value):
        if not value:
            return uuid.uuid4()
        return value

    @staticmethod
    def string_to_base64(string: Optional[str] = None) -> bytes:
        if not string:
            return base64.b64encode(b"")
        return base64.b64encode(string.encode("utf-8"))

    @staticmethod
    def base64_to_string(bytes_obj: Optional[bytes] = None) -> str:
        if not bytes_obj:
            return ""
        return base64.b64decode(bytes_obj).decode("utf-8")


class Command(BaseMessage):
    type: CommandType
    payload: Optional[bytes] = None
    arguments: Optional[List[str]] = None
    signature: Optional[bytes] = None

    # Because that would break the signature
    def __setattr__(self, *_, **__):
        raise ValueError("Fields cannot be modified after initialization")

    def __delattr__(self, *_, **__):
        raise ValueError("Fields cannot be deleted after initialization")

    def get_payload(self) -> str:
        return self.base64_to_string(self.payload)

    @validator("signature", always=True)
    def sign_signature(cls, value, values: Dict[str, Any]):
        if not value:
            return cls.generate_signature(values)
        return value

    @staticmethod
    def generate_signature(values: Dict[str, Any], secret_key=SECRET_KEY):
        data = json.dumps(values, default=str).encode("utf-8")
        signature = hmac.new(secret_key.encode("utf-8"), data, hashlib.sha256).digest()
        return base64.b64encode(signature)

    def validate_signature(self, secret_key=SECRET_KEY) -> bool:
        received_signature = self.signature
        computed_signature = self.generate_signature(
            self.model_dump(exclude={"signature"}), secret_key
        )

        if secrets.compare_digest(received_signature, computed_signature):  # type: ignore
            return True
        return False


class StatusType(Enum):
    HEARTBEAT = 1
    RECEIVED = 2
    INITIALIZED = 3
    RUNNING = 4
    FINISHED = 5
    ERROR = 6


class Message(BaseMessage):
    status: StatusType
    result: Optional[bytes] = None

    def get_result(self) -> str:
        return self.base64_to_string(self.result)
