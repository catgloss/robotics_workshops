"""ASR flask app."""

import os
import logging
from uuid import uuid4
from flask import Flask, request, jsonify

from transformers import logging as tlg
from speechbrain.pretrained import EncoderClassifier

from transcribers.transcriber_manager import TranscriberManager
from utils.db import ASR_DB
from utils.task import Task
from utils.file import check_file_type, save_file
from utils.pubsub import pubsub_helper
from utils.log import setup_logging
from constants import (
    LOG_FILE_PATH,
    NORMAL,
    INSTANT,
    BAD_REQUEST_CODE,
    SUCCESS_CODE,
    GET,
    POST,
    MP3_EXT,
    WAV_EXT,
)


# Logging.
LOGGER = logging.getLogger(__name__)
setup_logging(log_path=LOG_FILE_PATH, print_level="INFO", logger=LOGGER)
tlg.set_verbosity_error()

app = Flask(__name__)

if not os.path.isdir("./pretrained_models"):
    os.mkdir("./pretrained_models")
transcriber_manager = TranscriberManager()
lang_detect = EncoderClassifier.from_hparams(
    source="TalTechNLP/voxlingua107-epaca-tdnn",
    savedir="./pretrained_models/encoder-classifier",
)
db = ASR_DB


def _handle_bad_request(request_, is_valid_file):
    """Handle bad request."""
    if request_.method == POST:
        if not is_valid_file:
            return jsonify({"message": "Invalid file type"}), BAD_REQUEST_CODE
    return jsonify({"message": "Use POST method"}), BAD_REQUEST_CODE


@app.route("/queue_task", methods=[GET, POST])
def queue_task():
    """Queue task endpoint."""
    unique_id = str(uuid4())
    file = request.files["audio_file"]
    is_valid_file, file_type = check_file_type(file)
    _handle_bad_request(request, is_valid_file)

    save_file(
        "./temp_audio_files/uploaded_file_" + unique_id,
        file,
        file_type,
    )

    path = os.path.abspath("./temp_audio_files/uploaded_file_" + unique_id + WAV_EXT)

    # Detect Language.
    signal = lang_detect.load_audio(
        "./temp_audio_files/uploaded_file_" + unique_id + MP3_EXT
    )
    prediction = lang_detect.classify_batch(signal)[3][0]

    db_entry = db.add_file(file, prediction)
    pubsub_helper.setup_queue(db_entry)
    try:
        return (
            jsonify(
                detected_language=prediction,
                db_object_id=db_entry,
                note="You will be notified when your results are available "
                + "via the pubsub broker "
                + "on the queue with the same name as the 'db_objectID'",
            ),
            201,
        )
    finally:
        task = Task(
            audio_file=path,
            object_id=db_entry,
            priority=NORMAL,
            language=prediction,
            mp3_filename="uploaded_file_" + unique_id + MP3_EXT,
            wav_filename="uploaded_file_" + unique_id + WAV_EXT,
        )
        transcriber_manager.enqueue_normal(task)


@app.route("/instant_transcribe", methods=[GET, POST])
def instant_transcribe():
    """Instant transcribe endpoint."""
    unique_id = str(uuid4())
    file = request.files["audio_file"]
    is_valid_file, file_type = check_file_type(file)
    _handle_bad_request(request, is_valid_file)

    save_file(
        "./temp_audio_files/uploaded_file_" + unique_id,
        file,
        file_type,
    )

    path = os.path.abspath("./temp_audio_files/uploaded_file_" + unique_id + WAV_EXT)

    # Detect Language.
    signal = lang_detect.load_audio(
        "./temp_audio_files/uploaded_file_" + unique_id + MP3_EXT
    )
    prediction = lang_detect.classify_batch(signal)[3][0]

    db_entry = db.add_file(file, prediction)
    task = Task(
        audio_file=path,
        object_id=db_entry,
        priority=INSTANT,
        language=prediction,
        mp3_filename="uploaded_file_" + unique_id + MP3_EXT,
        wav_filename="uploaded_file_" + unique_id + WAV_EXT,
    )

    transcriber_manager.enqueue_instant(task)
    while not task.complete:
        pass
    LOGGER.info("Results ready!")

    return jsonify(db_object_id=db_entry, result=task.results), SUCCESS_CODE


@app.route("/get_results", methods=[GET])
def get_results():
    """Get results endpoint."""
    object_id = str(request.args.get("db_object_id"))

    if len(object_id) == 0 or object_id == "None":
        return jsonify(result="Results not found"), BAD_REQUEST_CODE

    result = db.get_result(object_id)

    if result is None:
        return jsonify(result="None or missing result"), BAD_REQUEST_CODE

    return jsonify(result=result["parsed_message"]), SUCCESS_CODE
