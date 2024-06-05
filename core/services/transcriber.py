import hashlib
import os
import re
import tempfile
import redis

from loguru import logger
from pytube import YouTube
from core.services.whisper import WhisperTranscriber


class TranscriptionService:
    def __init__(self, api_key: str, directory_path: str, redis_host: str, redis_port: int):
        self.api_key = api_key
        self.directory_path = directory_path
        self.transcriber = WhisperTranscriber(api_key=api_key, model_size="base.en")
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        logger.info("TranscriptionService initialized with directory path: {}", directory_path)

    @staticmethod
    def parse_combined_transcriptions(combined_transcriptions: str) -> list[tuple[str, str]]:
        pattern = r"\[(\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3})\]  (.+?)(?=\[|$)"
        matches = re.findall(pattern, combined_transcriptions)
        logger.info("Parsed combined transcriptions into {} segments", len(matches))
        return [(match[0], match[1]) for match in matches]

    def transcribe_one_file(self, file: str, return_only_vtt_transcription: bool = False) -> list[tuple[str, str]]:
        if not file.endswith((".mp3", ".wav", ".m4a", ".mp4", ".flac", ".mp4")):
            logger.error("Unsupported file type: {}", file)
            raise ValueError(f"Unsupported file type: {file}")

        logger.info("Starting transcription for file: {}", file)

        try:
            transcribed_texts, _, combined_transcriptions, _ = self.transcriber.transcribe_audio_with_timestamps(file)

            if return_only_vtt_transcription:
                logger.info("Returning only VTT transcription for file: {}", file)
                return " \n[".join(combined_transcriptions.split(" ["))

            logger.info("Transcription completed for file: {}", file)
            return self.parse_combined_transcriptions(combined_transcriptions)

        except Exception as e:
            error_message = str(e)

            if "Failed to load audio" in error_message or "Output file #0 does not contain any stream" in error_message:
                logger.error("Transcription failed: {}", error_message)
                raise ValueError("Most likely the video doesn't contain audio.") from e
            else:
                logger.error("An unexpected error occurred during transcription: {}", error_message)
                raise RuntimeError("An unexpected error occurred during transcription.") from e
            
    def transcribe_media_content(self, content: bytes, filename: str) -> str:
        content_hash = hashlib.md5(content).hexdigest()
        cached_transcription = self.redis_client.get(content_hash)
        
        if cached_transcription:
            logger.info("Returning cached transcription for file: {}", filename)
            return cached_transcription
    
        logger.info("Creating temporary file for transcription: {}", filename)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1], mode='wb') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            transcription = self.transcribe_one_file(temp_file_path)
            logger.info("Transcription completed for temporary file: {}", filename)
            self.redis_client.set(content_hash, transcription)
            return transcription
        
        finally:
            os.remove(temp_file_path)
            logger.info("Temporary file deleted: {}", temp_file_path)

    def transcribe_youtube_video(self, url: str, return_only_vtt_transcription: bool = False) -> str:
        logger.info("Downloading YouTube video: {}", url)
        yt = YouTube(url)
        video_id = yt.video_id
        cached_transcription = self.redis_client.get(video_id)
        
        if cached_transcription:
            logger.info("Returning cached transcription for video: {}", url)
            return cached_transcription

        stream = yt.streams.filter(only_audio=True).first()
        temp_file_path = stream.download(output_path=self.directory_path)
        
        try:
            transcription = self.transcribe_one_file(temp_file_path, return_only_vtt_transcription)
            logger.info("Transcription completed for YouTube video: {}", url)
            self.redis_client.set(video_id, transcription)
            return transcription
        
        finally:
            os.remove(temp_file_path)
            logger.info("Temporary file deleted: {}", temp_file_path)
