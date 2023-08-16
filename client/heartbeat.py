import base64
import json
import os
import socket
from time import sleep

from client_id import get_client_identifier
from logger import keyboard_interrupt_handler
from schema import Message, StatusType
from tasks import send_message


@keyboard_interrupt_handler
def heartbeat(url: str, interval: int):
    client_id = get_client_identifier()

    base64_encoded_info = base64.b64encode(
        json.dumps({"os": os.name, "hostname": socket.gethostname()}).encode("utf-8")
    )
    while True:
        send_message(
            Message(
                identifier=client_id,
                status=StatusType.HEARTBEAT,
                result=base64_encoded_info,
            ),
            url=url,
        )
        sleep(interval)
