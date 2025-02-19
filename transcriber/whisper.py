import torch
import numpy as np
from transformers import WhisperProcessor, WhisperForConditionalGeneration


class WhisperTranscribe:
    def __init__(self) -> None:
        self.processor = WhisperProcessor.from_pretrained("openai/whisper-small")
        self.model = WhisperForConditionalGeneration.from_pretrained(
            "openai/whisper-small"
        )
        # Disable forced decoder IDs to allow language detection
        self.model.config.forced_decoder_ids = None

    def split_audio_into_chunks(self, audio_data, sample_rate, chunk_duration=30):
        chunk_size = chunk_duration * sample_rate
        return [
            audio_data[i : i + chunk_size]
            for i in range(0, len(audio_data), chunk_size)
        ]

    def transcribe_audio(self, chunk, sample_rate=16000):
        audio_array = np.frombuffer(chunk, dtype=np.int16).astype(np.float32)

        # Normalize audio to the range [-1, 1]
        audio_array /= np.iinfo(np.int16).max

        inputs = self.processor(
            audio_array, sampling_rate=sample_rate, return_tensors="pt"
        )

        with torch.no_grad():
            predicted_ids = self.model.generate(inputs["input_features"])

        transcription = self.processor.batch_decode(
            predicted_ids, skip_special_tokens=True
        )[0]
        return transcription
