import uuid
from time import sleep

import requests
from logger import keyboard_interrupt_handler
from schema import Message, StatusType
from settings import BEACON_INTERVAL_SECONDS, REMOTE_SERVER


@keyboard_interrupt_handler
def beacon(server: str, interval: int):
    while True:
        headers = {"Content-type": "application/json"}

        try:
            response = requests.post(
                server,
                data=Message(
                    identifier=uuid.uuid4(), status=StatusType.BEACON
                ).model_dump_json(),
                headers=headers,
                timeout=1,
            )
            if response.status_code == 200:  # noqa: PLR2004
                print("Sent heartbeat to server")
            else:
                print("Failed to send heartbeat. Status code:", response.status_code)
        except requests.exceptions.RequestException as e:
            print("Error sending heartbeat:", e)

        sleep(interval)


if __name__ == "__main__":
    beacon(server=REMOTE_SERVER, interval=BEACON_INTERVAL_SECONDS)
