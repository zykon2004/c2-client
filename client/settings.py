from typing import Literal

from decouple import config

SECRET_KEY = config(
    "SECRET_KEY", default="qonOUAf/wwonkxviM+P6uNBpoOjUpmoX88YHA+EwLkc="
)
PROTOCOL: Literal["http", "https"] = config("PROTOCOL", default="http")
REMOTE_SERVER_HOST = config("REMOTE_SERVER_HOST", default="localhost")
REMOTE_SERVER_PORT = config("REMOTE_SERVER_PORT", default=8080, cast=int)
CLIENT_PORT = config("CLIENT_PORT", default=8070, cast=int)
HEARTBEAT_INTERVAL_SECONDS = config("HEARTBEAT_INTERVAL_SECONDS", default=5, cast=int)
REQUEST_TIMEOUT = config("REQUEST_TIMEOUT", default=5, cast=int)

REMOTE_SERVER_BASE_URL = f"{PROTOCOL}://{REMOTE_SERVER_HOST}:{REMOTE_SERVER_PORT}"
