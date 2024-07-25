from dotenv import load_dotenv
import os
from openai import OpenAI
from pathlib import Path
import openai

load_dotenv()
API_KEY = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key=API_KEY)

speech_file_path = Path(__file__).parent / "audio/speech.mp3"
response = openai.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="The quick brown fox jumped over the lazy dog."
)
response.stream_to_file(speech_file_path)
