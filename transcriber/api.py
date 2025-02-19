import io
import logging
import wave
from concurrent.futures import ThreadPoolExecutor

import grpc
import transcribe_pb2
import transcribe_pb2_grpc
from googletrans import Translator
from pydub import AudioSegment
from whisper import WhisperTranscribe
from whisper_hindi import HindiWhisperTranscribe
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


async def translate_text(text: str):
    async with Translator() as translator:
        result = await translator.translate(text, src="hindi", dest="english")
        return result.text


class AudioServiceServicer(transcribe_pb2_grpc.AudioServiceServicer):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.transcriber = WhisperTranscribe()
        self.hindi_transcriber = None

    def cal_chunk_size(self, audio_data, seconds=30):
        try:
            with wave.open(io.BytesIO(audio_data), "rb") as wav_file:
                sample_rate = wav_file.getframerate()
                bit_depth = wav_file.getsampwidth() * 8
                num_channels = wav_file.getnchannels()
                bytes_per_second = (sample_rate * bit_depth * num_channels) // 8
                return bytes_per_second * seconds
        except wave.Error as e:
            self.logger.warning(f"Not enough data to parse WAV header: {e}")
            return 0

    def TranscribeAudio(self, request_iterator, context):
        audio_data = bytearray()
        text = ""

        for req in request_iterator:
            audio_data.extend(req.audio_data)

        print("Starting to transcribe")
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=req.format)
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
            wave_data = audio.export(format="wav").read()
            chunk_size = self.cal_chunk_size(wave_data)

            while len(wave_data) >= chunk_size:
                chunk = wave_data[:chunk_size]
                wave_data = wave_data[chunk_size:]

                self.logger.info("Transcribing 30-second chunk...")
                transcription = str(self.transcriber.transcribe_audio(chunk))
                text += transcription

            if wave_data:
                self.logger.info("Transcribing remaining audio...")
                text += str(self.transcriber.transcribe_audio(wave_data))

            print(text)
            # text = asyncio.run(translate_text(text))
            # print(text)
            return transcribe_pb2.TranscribeResponse(status="Success", message=text)
        except Exception as e:
            self.logger.error(f"Error during transcription: {e}")
            # context.set_code(grpc.StatusCode.INTERNAL)
            # context.set_details(f"Error: {e}")
            return transcribe_pb2.TranscribeResponse(status="Error", message=str(e))

    def HindiTranscribeAudio(self, request_iterator, context):
        if self.hindi_transcriber is None:
            self.hindi_transcriber = HindiWhisperTranscribe()
        audio_data = bytearray()
        text = ""

        for req in request_iterator:
            audio_data.extend(req.audio_data)

        print("Starting to transcribe")
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format="webm")
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
            wave_data = audio.export(format="wav").read()
            chunk_size = self.cal_chunk_size(wave_data)

            while len(wave_data) >= chunk_size:
                chunk = wave_data[:chunk_size]
                wave_data = wave_data[chunk_size:]

                self.logger.info("Transcribing 30-second chunk...")
                transcription = str(self.hindi_transcriber.transcribe_audio(chunk))
                text += transcription

            if wave_data:
                self.logger.info("Transcribing remaining audio...")
                text += str(self.hindi_transcriber.transcribe_audio(wave_data))

            print(text)
            text = asyncio.run(translate_text(text))
            print(text)
            return transcribe_pb2.TranscribeResponse(status="Success", message=text)
        except Exception as e:
            self.logger.error(f"Error during transcription: {e}")
            return transcribe_pb2.TranscribeResponse(status="Error", message=str(e))


def serve():
    server = grpc.server(
        thread_pool=ThreadPoolExecutor(max_workers=10),
    )
    audio_server = AudioServiceServicer()
    transcribe_pb2_grpc.add_AudioServiceServicer_to_server(audio_server, server)

    server.add_insecure_port("[::]:50052")

    server.start()
    audio_server.logger.info("Audio server is running on port 50052...")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve()
