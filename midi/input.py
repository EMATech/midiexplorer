import multiprocessing
import threading
import time

import mido

from gui.config import START_TIME
from gui.logger import Logger

previous_timestamp = START_TIME
lock = threading.Lock()
queue = multiprocessing.SimpleQueue()


def receive_callback(midi_message: mido.Message) -> None:
    """
    MIDI data receive in "Callback" mode.

    Recommended.
    """
    logger = Logger()

    with lock:
        timestamp = time.time()
        logger.log_debug(f"Callback data: {midi_message}")
        queue.put((timestamp, midi_message))
