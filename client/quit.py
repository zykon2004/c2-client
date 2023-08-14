import logging
import os
import signal
from typing import List

# from schema import Message
# import requests
# from settings import REMOTE_SERVER


def quit_app(pids_to_kill: List[int]) -> None:
    for pid in pids_to_kill:
        logging.info("Killed PID %s", pid)
        os.kill(pid, signal.SIGTERM)
