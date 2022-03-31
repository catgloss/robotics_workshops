"""ASR Streamlit app."""

import os
import logging
import logging.handlers
import queue
import time
from pathlib import Path
import json
import requests
import pika
from requests_toolbelt.multipart.encoder import MultipartEncoder

import numpy as np
import pydub
import torchaudio
import streamlit as st
import plotly.express as px
import pandas as pd

from streamlit_webrtc import (
    ClientSettings,
    WebRtcMode,
    webrtc_streamer,
)

from utils.log import setup_logging
from constants import LOG_FILE_PATH
from transcribers.live_transcriber import LiveEnglishTranscriber, normalize_input


# Logging.
LOGGER = logging.getLogger(__name__)
setup_logging(log_path=LOG_FILE_PATH, print_level="INFO", logger=LOGGER)


HERE = Path(__file__).parent
DEFAULT_SAMPLE_RATE = 16000
BUFFER_SIZE = 64000
_QUEUE_TRANSCRIBE_ENDPOINT = "http://localhost:5000/queue_task"

transcribed = None


@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def _load_transcriber():
    return LiveEnglishTranscriber()


def run_app() -> None:
    """Run app."""
    st.header("Automatic Speech Recognition Service")
    st.subheader("Reference Implementation Demo")
    record = "Record Audio"
    upload = "Upload Audio"
    app_mode = st.selectbox("Choose Audio Input Mode", [record, upload])
    transcriber = _load_transcriber()
    if app_mode == record:
        live_transcribe(transcriber)
    elif app_mode == upload:
        queue_transcribe()


def generate_plot(signal_plot, audio_signal):
    """Create plot of audio input signal."""
    dataframe = pd.DataFrame(audio_signal)
    fig = px.line(dataframe, x=dataframe.index, y=0, render_mode="webgl")
    fig.update_layout(
        height=250,
        margin_r=0,
        margin_l=0,
        margin_t=0,
        yaxis_title="",
        yaxis_fixedrange=True,
    )

    signal_plot.write(fig)


def send_audio_to_transcription_queue(audio_file) -> str:
    """Send example audio file for transcription (Normal queue)."""
    with open(audio_file, "rb") as file_handle:
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
        global transcribed
        LOGGER.info(" [x] Received %r", body)
        transcribed = json.loads(body.decode('utf-8'))["parsed_message"]
        channel.queue_delete(queue=queue_name)

    channel.basic_consume(
        queue=queue_name, on_message_callback=_callback, auto_ack=True
    )
    LOGGER.info(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()
    if transcribed:
        return transcribed


def queue_transcribe():
    """Send to queue for transcription."""
    text_output = st.empty()
    signal_plot = st.empty()
    status_indicator = st.empty()

    uploaded_file = st.file_uploader("Upload audio file (wav/mp3)")
    status_indicator.write("Loading...")
    if uploaded_file is not None:
        file_details = {
            "filename": uploaded_file.name,
            "filetype": uploaded_file.type,
            "filesize": uploaded_file.size,
        }
        st.write(file_details)
        with open((uploaded_file.name), "wb") as file_handle:
            file_handle.write(uploaded_file.getbuffer())
        with open(uploaded_file.name, "rb") as file_handle:
            audio_bytes = file_handle.read()
        st.audio(audio_bytes, format="audio/ogg")
        status_indicator.write("Saved file to database!")
        signal, _ = torchaudio.load(uploaded_file.name, channels_first=False)
        generate_plot(signal_plot, signal)

        text = send_audio_to_transcription_queue(uploaded_file.name)
        text_output.markdown(f"**Text:** {text}")


def live_transcribe(live_transcriber):
    """Send audio from live stream source for instant transcription."""
    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=2048,
        client_settings=ClientSettings(
            rtc_configuration={
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            },
            media_stream_constraints={"video": False, "audio": True},
        ),
    )

    signal_plot = st.empty()
    status_indicator = st.empty()
    text_output = st.empty()
    sound_chunk = pydub.AudioSegment.empty()

    if not webrtc_ctx.state.playing:
        return

    status_indicator.write("Loading...")

    while True:
        if webrtc_ctx.audio_receiver:
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                time.sleep(0.1)
                status_indicator.write("No frame arrived.")
                continue

            status_indicator.write("Running. Say something!")

            for audio_frame in audio_frames:
                sound = pydub.AudioSegment(
                    data=audio_frame.to_ndarray().tobytes(),
                    sample_width=audio_frame.format.bytes,
                    frame_rate=audio_frame.sample_rate,
                    channels=len(audio_frame.layout.channels),
                )
                sound_chunk += sound

            if len(sound_chunk) > 0:
                sound_chunk = sound_chunk.set_channels(1).set_frame_rate(
                    DEFAULT_SAMPLE_RATE
                )
                buffer = np.array(sound_chunk.get_array_of_samples()).astype(np.double)
                LOGGER.info(len(buffer))
                if len(buffer) >= BUFFER_SIZE:
                    buffer = normalize_input(buffer)
                    generate_plot(signal_plot, buffer)
                    text = live_transcriber.transcribe(buffer)
                    text_output.markdown(f"**Text:** {text}")
                    sound_chunk = pydub.AudioSegment.empty()

        else:
            status_indicator.write("AudioReceiver is not set. Abort.")
            break


if __name__ == "__main__":
    DEBUG = os.environ.get("DEBUG", "false").lower() not in ["false", "no", "0"]
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)7s from %(name)s in %(pathname)s:%(lineno)d: "
        "%(message)s",
        force=True,
    )
    st_webrtc_logger = logging.getLogger("streamlit_webrtc")
    st_webrtc_logger.setLevel(logging.DEBUG)
    fsevents_logger = logging.getLogger("fsevents")
    fsevents_logger.setLevel(logging.WARNING)

    run_app()
