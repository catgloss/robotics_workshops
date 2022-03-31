"""Transcriber models."""

from speechbrain.pretrained import EncoderDecoderASR, EncoderASR
from asrecognition import ASREngine

from transcribers.base import BaseTranscriber


def english_transcriber(normal_queue, instant_queue):
    """English transcriber."""
    return BaseTranscriber(
        EncoderDecoderASR.from_hparams(
            source="speechbrain/asr-wav2vec2-commonvoice-en",
            savedir="./pretrained_models/asr-wav2vec2-commonvoice-en",
        ),
        normal_queue,
        instant_queue,
    )

def french_transcriber(normal_queue, instant_queue):
    """French transcriber."""
    return BaseTranscriber(
        EncoderASR.from_hparams(
            source="speechbrain/asr-wav2vec2-commonvoice-fr",
            savedir="./pretrained_models/asr-wav2vec2-commonvoice-fr",
        ),
        normal_queue,
        instant_queue,
    )

def italian_transcriber(normal_queue, instant_queue):
    """Italian transcriber."""
    return BaseTranscriber(
        EncoderDecoderASR.from_hparams(
            source="speechbrain/asr-wav2vec2-commonvoice-it",
            savedir="./pretrained_models/asr-wav2vec2-commonvoice-it",
        ),
        normal_queue,
        instant_queue,
    )
 

class HuggingFaceTranscriber(BaseTranscriber):
    def __init__(self, asr_model, normal_queue, instant_queue):
        super().__init__(asr_model,normal_queue, instant_queue)
        
    def transcribe(self, filepath):
        return self.asr_model.transcribe([filepath])


def spanish_transcriber(normal_queue, instant_queue):
    """Spanish transcriber."""
    return HuggingFaceTranscriber(
        ASREngine("es"),
        normal_queue,
        instant_queue,
    )
