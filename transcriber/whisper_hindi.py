from transformers import pipeline


class HindiWhisperTranscribe:
    def __init__(self) -> None:
        self.transcribe = pipeline(
            task="automatic-speech-recognition",
            model="vasista22/whisper-hindi-small",
            chunk_length_s=30,
        )
        # self.transcribe.model.config.forced_decoder_ids = self.transcribe.tokenizer.get_decoder_prompt_ids(language="hi", task="transcribe")
        self.transcribe.model.config.forced_decoder_ids = None

    def transcribe_audio(self, chunk, sample_rate=16000):
        return self.transcribe(chunk)["text"]
