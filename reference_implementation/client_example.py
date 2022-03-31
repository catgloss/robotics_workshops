"""An example of how to use python as a client to the ASR service."""

import os
import logging
import sys
import json
import requests
import pika
from requests_toolbelt.multipart.encoder import MultipartEncoder

from asr.utils.log import setup_logging
from asr.constants import LOG_FILE_PATH, ENGLISH


# Logging.
LOGGER = logging.getLogger(__name__)
setup_logging(log_path=LOG_FILE_PATH, print_level="INFO", logger=LOGGER)


_QUEUE_TRANSCRIBE_ENDPOINT = "http://localhost:5000/queue_task"
_INSTANT_TRANSCRIBE_ENDPOINT = "http://localhost:5000/instant_transcribe"
_GET_RESULTS_ENDPOINT = "http://localhost:5000/get_results"
_EXAMPLE_RECORDING_FILE = "./audio_samples/en.wav"


def send_audio_to_transcription_queue() -> None:
    """Send example audio file for transcription (Normal queue)."""
    with open(_EXAMPLE_RECORDING_FILE, "rb") as file_handle:
        mp_encoder = MultipartEncoder(
            fields={
                "audio_file": ("spam.txt", file_handle, "audio/wav"),
            }
        )
        response = requests.post(
            _QUEUE_TRANSCRIBE_ENDPOINT,
            data=mp_encoder,
            headers={"Content-Type": mp_encoder.content_type},
        )
    response_json = json.loads(response.text)
    LOGGER.info(response_json)

    queue_name = response_json["db_object_id"]

    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    def _callback(
        channel, method, header_frame, body
    ):  # pylint: disable=unused-argument
        LOGGER.info(" [x] Received %r", body.decode("unicode_escape"))
        channel.queue_delete(queue=queue_name)

    channel.basic_consume(
        queue=queue_name, on_message_callback=_callback, auto_ack=True
    )
    LOGGER.info(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


def send_audio_for_instant_transcription() -> None:
    """Send example audio file for transcription (Instant transcription queue)."""
    with open(_EXAMPLE_RECORDING_FILE, "rb") as file_handle:
        mp_encoder = MultipartEncoder(
            fields={
                "audio_file": ("spam.txt", file_handle, "audio/wav"),
                "language": ENGLISH,
            }
        )
        response = requests.post(
            _INSTANT_TRANSCRIBE_ENDPOINT,
            data=mp_encoder,
            headers={"Content-Type": mp_encoder.content_type},
        )
    response_json = json.loads(response.text)
    LOGGER.info(response_json)


def get_previously_added_results(db_object_id: str) -> None:
    """Get results from the DB that was previously added.

    Parameters
    ----------
    db_object_id: str
        ID of previously stored results document in database.
    """
    response = requests.get(
        _GET_RESULTS_ENDPOINT,
        params={"db_object_id": db_object_id},
    )
    response_json = json.loads(response.text)
    LOGGER.info(response_json)


if __name__ == "__main__":
    try:
        # send_audio_for_instant_transcription()
        send_audio_to_transcription_queue()
        # get_previously_added_results("623352997f7e437abcf65962")
    except KeyboardInterrupt:
        LOGGER.info("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)  # pylint:disable=protected-access
