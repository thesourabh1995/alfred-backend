from openai import OpenAI
from config import OPENAI_API_KEY


class TranscriptionService:
    def __init__(self):
        # Use the API key from environment variable or directly in the code
        api_key = OPENAI_API_KEY  # Fetch API key from environment variable
        if not api_key:
            raise ValueError("OpenAI API key must be set in the environment variable 'OPENAI_API_KEY'")

        self.client = OpenAI(api_key=api_key)

    def transcribe_audio(self, audio_file_path: str) -> str:
        # Open the audio file and send it to the Whisper API for transcription
        with open(audio_file_path, "rb") as audio_file:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            return transcription.text
