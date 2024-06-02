import os
import whisper

from datetime import timedelta


class WhisperTranscriber:
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
    SILENCE_THRESH = -40
    SILENCE_LEN = 500
    SAVE_DIR = "downloaded_audio"

    def __init__(self, api_key, model_size="base.en"):
        self.api_key = api_key
        self.model_size = model_size
        self.model = whisper.load_model(self.model_size)

    def transcribe_audio_with_timestamps(self, audio_file_path):
        model = whisper.load_model(self.model_size)
        result = model.transcribe(audio_file_path, verbose=True)
        segments = result.get("segments")
        transcribed_texts = " ".join([segment["text"] for segment in segments])
        formatted_timestamps = [
            "[{start} --> {end}]".format(
                start=self.format_timestamp(segment["start"]),
                end=self.format_timestamp(segment["end"]),
            )
            for segment in segments
        ]
        combined_transcriptions = " ".join(
            [f"{formatted_timestamps[i]} {segments[i]['text']}" for i in range(len(segments))]
        )
        file_name = os.path.basename(audio_file_path)
        return transcribed_texts, " ".join(formatted_timestamps), combined_transcriptions, file_name

    def format_timestamp(self, seconds):
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = td.microseconds // 1000
        return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
