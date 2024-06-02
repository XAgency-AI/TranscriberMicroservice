import os
import whisper
from datetime import timedelta
from loguru import logger


class WhisperTranscriber:
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
    SILENCE_THRESH = -40
    SILENCE_LEN = 500
    SAVE_DIR = "downloaded_audio"

    def __init__(self, api_key: str, model_size: str = "base.en"):
        """
        Initialize the WhisperTranscriber with the given API key and model size.

        Args:
            api_key (str): The API key for the Whisper service.
            model_size (str): The size of the Whisper model to load.
        """
        self.api_key = api_key
        self.model_size = model_size
        self.model = whisper.load_model(self.model_size)
        logger.info(f"Whisper model '{self.model_size}' loaded successfully.")

    def transcribe_audio_with_timestamps(self, audio_file_path: str) -> tuple[str, str, str, str]:
        """
        Transcribe the audio file and return the transcribed text along with timestamps.

        Args:
            audio_file_path (str): The path to the audio file to transcribe.

        Returns:
            tuple: A tuple containing the transcribed texts, formatted timestamps,
            combined transcriptions, and file name.
        """
        try:
            logger.info(f"Starting transcription for file: {audio_file_path}")
            result = self.model.transcribe(audio_file_path, verbose=True)
            segments = result.get("segments")
            transcribed_texts = " ".join([segment["text"] for segment in segments])
            formatted_timestamps = [
                f"[{self.format_timestamp(segment['start'])} --> {self.format_timestamp(segment['end'])}]"
                for segment in segments
            ]
            combined_transcriptions = " ".join(
                [f"{formatted_timestamps[i]} {segments[i]['text']}" for i in range(len(segments))]
            )
            file_name = os.path.basename(audio_file_path)
            logger.info(f"Transcription completed for file: {audio_file_path}")
            return transcribed_texts, " ".join(formatted_timestamps), combined_transcriptions, file_name
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise

    def format_timestamp(self, seconds: float) -> str:
        """
        Format the given time in seconds to a timestamp string.

        Args:
            seconds (float): The time in seconds to format.

        Returns:
            str: The formatted timestamp string.
        """
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = td.microseconds // 1000
        return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
