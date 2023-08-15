import base64
import logging
import os
import signal
import subprocess
from typing import Iterable, Tuple

import requests
from schema import Command, Message, StatusType
from settings import REMOTE_SERVER


def quit_app(pids_to_kill: Iterable[int]) -> None:
    for pid in pids_to_kill:
        logging.info("Killed PID %s", pid)
        os.kill(pid, signal.SIGTERM)


def run_command(command: Command) -> Tuple[bytes, bytes]:
    logging.debug("Received Command: %s", command)
    if not command.payload:
        raise ValueError(f"Missing payload for command {command.identifier}")

    process_args = (
        (command.payload,)
        if not command.arguments
        else (command.payload, *command.arguments)
    )

    try:
        logging.info(
            "Executing Payload: %s with args: %s", command.payload, command.arguments
        )
        send_message(
            Message(identifier=command.identifier, status=StatusType.INITIALIZED)
        )
        process = subprocess.Popen(
            args=process_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )

        send_message(Message(identifier=command.identifier, status=StatusType.RUNNING))
        stdout, stderr = process.communicate()

        if stderr:
            send_message(
                Message(
                    identifier=command.identifier,
                    status=StatusType.ERROR,
                    result=base64.encodebytes(stderr),
                )
            )
        else:
            send_message(
                Message(
                    identifier=command.identifier,
                    status=StatusType.FINISHED,
                    result=base64.encodebytes(stdout),
                )
            )
        return stdout, stderr

    except Exception as e:
        send_message(
            Message(
                identifier=command.identifier,
                status=StatusType.ERROR,
                result=base64.encodebytes(str(e).encode()),
            )
        )
        return b"", str(e).encode()


def send_message(message: Message, server: str = REMOTE_SERVER):
    headers = {"Content-type": "application/json"}
    message_type = "heartbeat" if message.status == StatusType.HEARTBEAT else "message"
    try:
        response = requests.post(
            url=server,
            data=message.model_dump_json(),
            headers=headers,
            timeout=1,
        )
        if response.status_code == 200:  # noqa: PLR2004
            logging.info("Successfully sent %s", message)
        else:
            logging.info(
                "Failed to send %s. Status code: %s", message_type, response.status_code
            )
    except requests.exceptions.RequestException as e:
        logging.error("Exception raised while sending %s: %s", message_type, str(e))
