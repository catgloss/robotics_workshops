"""An example model transcriber to use for live demo using streamlit."""

import numpy as np
import torch

from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor


DEFAULT_SAMPLE_RATE = 16000
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def normalize_input(audio_input: np.ndarray) -> np.ndarray:
    """Normalize input array."""
    normalized = audio_input / np.max(np.abs(audio_input), axis=0)
    return normalized


class LiveEnglishTranscriber:  # pylint: disable=too-few-public-methods
    """An example of a different model to use as transcriber for streamlit app."""

    def __init__(self):
        """Instantiate."""
        self._processor = Wav2Vec2Processor.from_pretrained(
            "facebook/wav2vec2-base-960h"
        )
        self._model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h").to(
            DEVICE
        )

    def transcribe(self, audio_input: np.ndarray) -> torch.Tensor:
        """Transcribe audio input.

        Parameters
        ----------
        audio_input: numpy.ndarray
            Input audio array.

        Returns
        -------
        torch.Tensor
            Transcribed model output.

        """
        return self._ctc_transcribe(audio_input)

    def _ctc_transcribe(self, audio_input: np.ndarray) -> torch.Tensor:
        input_values = self._processor(
            audio_input, sampling_rate=DEFAULT_SAMPLE_RATE, return_tensors="pt"
        ).input_values

        logits = self._model(input_values.to(DEVICE)).logits
        predicted_ids = torch.argmax(logits, dim=-1)

        return self._processor.decode(predicted_ids[0], skip_special_tokens=True)
