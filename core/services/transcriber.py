import os
import re
import tempfile

from core.services.whisper import WhisperTranscriber


class TranscriptionService:
    def __init__(self, api_key: str, directory_path: str):
        self.api_key = api_key
        self.directory_path = directory_path
        self.transcriber = WhisperTranscriber(api_key=api_key, model_size="base.en")

    @staticmethod
    def parse_combined_transcriptions(combined_transcriptions: str) -> list[tuple[str, str]]:
        pattern = r"\[(\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3})\]  (.+?)(?=\[|$)"
        matches = re.findall(pattern, combined_transcriptions)
        return [(match[0], match[1]) for match in matches]

    def transcribe_one_file(self, file: str, return_only_vtt_transcription: bool = False) -> str:
        if not file.endswith((".mp3", ".wav", ".m4a", ".mp4", ".flac")):
            return ""
        transcribed_texts, _, combined_transcriptions, _ = self.transcriber.transcribe_audio_with_timestamps(file)
        if return_only_vtt_transcription:
            return " \n[".join(combined_transcriptions.split(" ["))
        return transcribed_texts

    def transcribe_media_content(self, content: bytes, filename: str) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        try:
            return self.transcribe_one_file(temp_file_path)
        finally:
            os.remove(temp_file_path)