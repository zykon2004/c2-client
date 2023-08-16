import logging
import os
from multiprocessing import Process, Queue
from typing import Iterable

import uvicorn
from fastapi import FastAPI, HTTPException
from heartbeat import heartbeat
from logger import LOGGING_CONFIG, keyboard_interrupt_handler, setup_logger
from schema import Command, CommandType, Message, StatusType
from settings import (
    CLIENT_PORT,
    HEARTBEAT_INTERVAL_SECONDS,
    REMOTE_SERVER_BASE_URL,
    SECRET_KEY,
)
from tasks import quit_app, run_command


@keyboard_interrupt_handler
def command_processor(queue: Queue, pids_to_kill_on_quit: Iterable[int]) -> None:
    while True:
        command = queue.get()
        if command.type == CommandType.RUN:
            run_command(command)

        if command.type == CommandType.KILL:
            current_process_pid = os.getpid()
            # if current_process_pid is first then it would kill
            # himself first and skip the rest
            quit_app((*pids_to_kill_on_quit, current_process_pid))


def create_listener(command_queue: Queue) -> FastAPI:
    app = FastAPI()

    @app.post("/run_command", response_model=Message)
    async def run_command(command: Command):
        if command.validate_signature(SECRET_KEY):
            # It seems that this way is used to communicate between processes
            # I have decided not to continue implementing it and sticking to using Queue
            # file_path = Path(PAYLOAD_DIRECTORY) / str(command.identifier) / ".json"
            # with open(file_path, 'w') as json_file:
            #     json.dump(
            #         command.model_dump_json(include={"payload", "arguments"}),
            #         json_file,
            #     )
            #     logging.info("Dumped %s", file_path)

            command_queue.put(command)
            return Message(identifier=command.identifier, status=StatusType.RECEIVED)
        else:
            logging.error("Invalid signature for command: %s", command)
            raise HTTPException(status_code=401, detail="Invalid signature")

    @app.post("/", response_model=None)
    async def get_heartbeat(msg: Message) -> None:
        # print(msg)
        ...

    return app


if __name__ == "__main__":
    setup_logger("c2-client")
    heartbeat_process = Process(
        target=heartbeat,
        kwargs=dict(url=REMOTE_SERVER_BASE_URL, interval=HEARTBEAT_INTERVAL_SECONDS),
    )
    heartbeat_process.start()

    command_queue: Queue = Queue()
    main_process_pid = os.getpid()
    command_executer = Process(
        target=command_processor,
        kwargs=dict(
            queue=command_queue,
            pids_to_kill_on_quit=[main_process_pid, heartbeat_process.pid],
        ),
    )
    command_executer.start()
    uvicorn.run(
        create_listener(command_queue),
        host="0.0.0.0",  # noqa: S104
        port=CLIENT_PORT,
        log_config=LOGGING_CONFIG,
        # ssl_keyfile=str(Path("../keys/key.pem")),
        # ssl_certfile=Path("../keys/cert.pem"),
    )
    command_executer.join()
    heartbeat_process.join()
