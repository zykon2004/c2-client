from time import sleep

from logger import keyboard_interrupt_handler
from schema import Message, StatusType
from tasks import send_message


@keyboard_interrupt_handler
def beacon(server: str, interval: int):
    while True:
        send_message(Message(status=StatusType.HEARTBEAT), server=server)
        sleep(interval)
