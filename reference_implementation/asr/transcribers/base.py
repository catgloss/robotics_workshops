"""Base transcriber class."""

import os
import logging
from datetime import datetime
import queue

import librosa

from utils.db import ASR_DB
from utils.pubsub import pubsub_helper
from utils.log import setup_logging
from constants import LOG_FILE_PATH, INSTANT, NORMAL


# Logging.
LOGGER = logging.getLogger(__name__)
setup_logging(log_path=LOG_FILE_PATH, print_level="INFO", logger=LOGGER)

_TIME_FMT = "%H:%M:%S"


class BaseTranscriber:
    """Base transcriber."""

    def __init__(self, asr_model, normal_queue, instant_queue):
        """Instantiate."""
        self.asr_model = asr_model
        self.normal_queue = normal_queue
        self.instant_queue = instant_queue

    def transcribe(self, filepath):
        """Instantly transcrible a file, accepts file path."""
        return self.asr_model.transcribe_file(filepath)

    def worker(self):
        """Working for transcriber (loop for transcription)."""
        task = False
        while True:
            if not self.instant_queue.empty():
                try:
                    task = self.instant_queue.get_nowait()
                except queue.Empty:
                    pass
            else:
                try:
                    task = self.normal_queue.get_nowait()
                except queue.Empty:
                    pass

            if task and not task.complete:
                LOGGER.info("Starting decoding...")

                start = datetime.now().strftime(_TIME_FMT)
                try:
                    output = self.transcribe(task.audio_file)
                except RuntimeError:
                    continue
                end = datetime.now().strftime(_TIME_FMT)
                tdelta = datetime.strptime(end, _TIME_FMT) - datetime.strptime(
                    start, _TIME_FMT
                )
                duration = librosa.get_duration(filename=task.audio_file)

                result = {
                    "parsed_message": output,
                    "audio_file_length": duration,
                    "detected_language": task.language,
                    "processing_time_seconds": tdelta.total_seconds(),
                }
                ASR_DB.add_results(result, task.language, task.object_id)
                task.mark_complete(result)

                if task.priority == INSTANT:
                    self.instant_queue.task_done()
                elif task.priority == NORMAL:
                    pubsub_helper.send_message(
                        queue_name=task.object_id, message_to_send=result
                    )
                _cleanup_task_files(task)


def _cleanup_task_files(task):
    LOGGER.info("Cleaning up temporary files...")
    if os.path.exists("./" + task.wav_filename):
        os.unlink("./" + task.wav_filename)
    if os.path.exists("./" + task.mp3_filename):
        os.unlink("./" + task.mp3_filename)
    if os.path.exists("./temp_audio_files/" + task.wav_filename):
        os.remove("./temp_audio_files/" + task.wav_filename)
    if os.path.exists("./temp_audio_files/" + task.mp3_filename):
        os.remove("./temp_audio_files/" + task.mp3_filename)
