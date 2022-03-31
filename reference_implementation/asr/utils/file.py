"""File utility functions."""


import os
from werkzeug.datastructures import FileStorage
from pydub import AudioSegment

from constants import WAV, MP3, AUDIO


def check_file_type(file: FileStorage) -> tuple:
    """Check mimetype (media type) of file.

    Parameters
    ----------
    file: FileStorage
        File container used to store input audio.

    Returns
    -------
    tuple
        (bool, str) where bool flag if input is audio type, MP3/WAV.

    """
    mime_type = str(file.mimetype)
    if AUDIO in mime_type:
        if WAV in mime_type:
            return True, WAV
        if MP3 in mime_type:
            return True, MP3
    return False, None


def save_file(file_path: str, file: FileStorage, file_type: str) -> None:
    """Convert and save alternative file type WAV <-> MP3.

    Parameters
    ----------
    file_path: str
        Path to save file.
    file: FileStorage
        File container used to store input audio.
    file_type: str
        Type of audio file.
    """
    if not os.path.isdir("./temp_audio_files"):
        os.mkdir("./temp_audio_files")

    file.save(file_path + "." + file_type)

    if file_type == WAV:
        other_file_type = MP3
    elif file_type == MP3:
        other_file_type = WAV

    AudioSegment.from_file(file_path + "." + file_type).export(
        file_path + "." + other_file_type, format=other_file_type
    )
