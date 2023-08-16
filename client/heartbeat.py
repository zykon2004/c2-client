from time import sleep

from client_id import get_client_identifier
from logger import keyboard_interrupt_handler
from schema import Message, StatusType
from tasks import send_message


@keyboard_interrupt_handler
def heartbeat(url: str, interval: int):
    client_id = get_client_identifier()
    while True:
        send_message(
            Message(identifier=client_id, status=StatusType.HEARTBEAT), url=url
        )
        sleep(interval)
