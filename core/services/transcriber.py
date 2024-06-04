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
        """
        Initialize the TranscriptionService with the given API key, directory path, and Redis connection.

        Args:
            api_key (str): The API key for the transcription service.
            directory_path (str): The directory path for temporary file storage.
            redis_host (str): The Redis host.
            redis_port (int): The Redis port.
        """
        self.api_key = api_key
        self.directory_path = directory_path
        self.transcriber = WhisperTranscriber(api_key=api_key, model_size="base.en")
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        logger.info("TranscriptionService initialized with directory path: {}", directory_path)

    @staticmethod
    def parse_combined_transcriptions(combined_transcriptions: str) -> list[tuple[str, str]]:
        """
        Parse combined transcriptions into a list of tuples containing timestamps and text.

        Args:
            combined_transcriptions (str): The combined transcriptions string.

        Returns:
            list[tuple[str, str]]: A list of tuples where each tuple contains a timestamp and the corresponding text.
        """
        pattern = r"\[(\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3})\]  (.+?)(?=\[|$)"
        matches = re.findall(pattern, combined_transcriptions)
        logger.info("Parsed combined transcriptions into {} segments", len(matches))
        return [(match[0], match[1]) for match in matches]

    def transcribe_one_file(self, file: str, return_only_vtt_transcription: bool = False) -> str:
        """
        Transcribe the given audio or video file.

        Args:
            file (str): The path to the file to transcribe.
            return_only_vtt_transcription (bool): Whether to return only the VTT transcription.

        Returns:
            str: The transcribed text.
        """
        if not file.endswith((".mp3", ".wav", ".m4a", ".mp4", ".flac")):
            logger.error("Unsupported file type: {}", file)
            return ""
        logger.info("Starting transcription for file: {}", file)
        transcribed_texts, _, combined_transcriptions, _ = self.transcriber.transcribe_audio_with_timestamps(file)
        if return_only_vtt_transcription:
            logger.info("Returning only VTT transcription for file: {}", file)
            return " \n[".join(combined_transcriptions.split(" ["))
        logger.info("Transcription completed for file: {}", file)
        return transcribed_texts

    def transcribe_media_content(self, content: bytes, filename: str) -> str:
        """
        Transcribe the given media content from bytes.

        Args:
            content (bytes): The media content to transcribe.
            filename (str): The name of the file being transcribed.

        Returns:
            str: The transcribed text.
        """
        # Generate a hash of the content to use as a cache key
        content_hash = hashlib.md5(content).hexdigest()
        
        # Check if the transcription is already cached
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
            
            # Cache the transcription
            self.redis_client.set(content_hash, transcription)
            
            return transcription
        finally:
                os.remove(temp_file_path)
                logger.info("Temporary file deleted: {}", temp_file_path)

    def transcribe_youtube_video(self, url: str, return_only_vtt_transcription: bool = False) -> str:
        """
        Download and transcribe a YouTube video.

        Args:
            url (str): The URL of the YouTube video.
            return_only_vtt_transcription (bool): Whether to return only the VTT transcription.

        Returns:
            str: The transcribed text with timestamps.
        """
        logger.info("Downloading YouTube video: {}", url)
        yt = YouTube(url)
        video_id = yt.video_id

        # Check if the transcription is already cached
        cached_transcription = self.redis_client.get(video_id)
        if cached_transcription:
            logger.info("Returning cached transcription for video: {}", url)
            return cached_transcription

        stream = yt.streams.filter(only_audio=True).first()
        temp_file_path = stream.download(output_path=self.directory_path)
        
        try:
            transcription = self.transcribe_one_file(temp_file_path, return_only_vtt_transcription)
            logger.info("Transcription completed for YouTube video: {}", url)
            # Cache the transcription
            self.redis_client.set(video_id, transcription)
            return transcription
        finally:
            os.remove(temp_file_path)
            logger.info("Temporary file deleted: {}", temp_file_path)
