"""Transcriber Manager."""

import logging
from queue import Queue
import threading

from transcribers.transcriber_models import english_transcriber, spanish_transcriber, italian_transcriber, french_transcriber
from utils.log import setup_logging
from constants import LOG_FILE_PATH, INSTANT, NORMAL, ENGLISH, SPANISH, ITALIAN, FRENCH


# Logging.
LOGGER = logging.getLogger(__name__)
setup_logging(log_path=LOG_FILE_PATH, print_level="INFO", logger=LOGGER)


_TRANSCRIBERS_MAP = {ENGLISH: english_transcriber, FRENCH: french_transcriber, SPANISH: spanish_transcriber, ITALIAN: italian_transcriber}


class TranscriberManager:
    """Transcriber manager module."""

    def __init__(self):
        """Instantiate."""
        self.transribers = {}
        self.queues = {INSTANT: {}, NORMAL: {}}

        for supported_language, transcriber in _TRANSCRIBERS_MAP.items():
            self.queues[INSTANT][supported_language] = Queue()
            self.queues[NORMAL][supported_language] = Queue()
            self.transribers[supported_language] = transcriber(
                self.queues[NORMAL][supported_language],
                self.queues[INSTANT][supported_language],
            )
            threading.Thread(
                target=self.transribers[supported_language].worker,
                daemon=True,
                name=supported_language + "worker",
            ).start()

    def transcribe_file(self, filepath, language):
        """Transcribe a file, accepts filepath and language."""
        if language not in _TRANSCRIBERS_MAP:
            LOGGER.error("Unsupported language detected!!")
            raise NotImplementedError
        return self.transribers[language].transcribe(filepath=filepath)

    def enqueue_normal(self, task):
        """Add a task to the normal queue."""
        if task.language in _TRANSCRIBERS_MAP:
            self.queues[NORMAL][task.language].put(task)
            return
        LOGGER.error("Unsupported language!!")

    def enqueue_instant(self, task):
        """Add a task to the instant queue."""
        if task.language in _TRANSCRIBERS_MAP:
            self.queues[INSTANT][task.language].put(task)
            return
        LOGGER.error("Unsupported language!!")
