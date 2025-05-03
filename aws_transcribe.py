import asyncio
import os

import boto3
import sounddevice as sd

from amazon_transcribe.auth import AwsCredentialsProvider
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent


# =========================
# Configuration Parameters
# =========================

# AWS region where the transcription service will run
AWS_REGION = "us-east-1"

# Language code used for transcription (e.g., 'en-US', 'pt-BR')
LANGUAGE_CODE = "pt-BR"

# Sample rate in Hertz (must match the audio device's settings and AWS limits)
SAMPLE_RATE_HZ = 16000

# Audio encoding format used for streaming (must be supported by AWS)
MEDIA_ENCODING = "pcm"

# Number of audio channels; AWS Transcribe requires mono (1)
CHANNELS = 1

# Data type of the audio stream (must align with MEDIA_ENCODING and device settings)
DTYPE = 'int16'

# Size of audio chunks (in frames) to read and send at a time
CHUNK_SIZE = 1024

# =========================
# AWS Credential Injection
# =========================
def export_credentials_from_profile(profile_name: str = None):
    """
    Exports AWS credentials from the specified profile or from the AWS_PROFILE environment variable,
    and sets them in the current process environment for use by libraries that require env-based auth.
    """
    # Try to get from environment if no profile was explicitly passed
    selected_profile = profile_name or os.environ.get("AWS_PROFILE")

    if not selected_profile:
        raise RuntimeError("No AWS profile provided and AWS_PROFILE environment variable is not set.")

    session = boto3.Session(profile_name=selected_profile)
    credentials = session.get_credentials()

    if credentials is None:
        raise RuntimeError(f"No credentials found for profile '{selected_profile}'.")

    frozen = credentials.get_frozen_credentials()

    # Set credentials as environment variables so they can be picked up by third-party libraries
    os.environ["AWS_ACCESS_KEY_ID"] = frozen.access_key
    os.environ["AWS_SECRET_ACCESS_KEY"] = frozen.secret_key
    if frozen.token:
        os.environ["AWS_SESSION_TOKEN"] = frozen.token

# Export credentials before any AWS client is initialized
export_credentials_from_profile()  # Optional: pass a profile name here

# =========================
# Transcript Event Handler
# =========================

class MyEventHandler(TranscriptResultStreamHandler):
    """
    Custom event handler to process transcription results from Amazon Transcribe.
    Displays partial and final transcriptions in the console.
    """
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            if result.is_partial:
                for alt in result.alternatives:
                    print(alt.transcript, end="\r")
            else:
                for alt in result.alternatives:
                    print(alt.transcript)

# =========================
# Microphone Audio Stream
# =========================

async def mic_stream():
    """
    Captures real-time audio from the default microphone input and yields it as byte chunks.
    """
    with sd.InputStream(samplerate=SAMPLE_RATE_HZ, channels=CHANNELS, dtype=DTYPE) as stream:
        while True:
            data, overflowed = stream.read(CHUNK_SIZE)
            yield data.tobytes()

# =========================
# Stream Audio to AWS
# =========================

async def write_chunks(stream):
    """
    Reads audio chunks from the microphone and sends them to the transcription stream.
    Ends the stream once input stops.
    """
    async for chunk in mic_stream():
        await stream.input_stream.send_audio_event(audio_chunk=chunk)
    await stream.input_stream.end_stream()

# =========================
# Transcription Workflow
# =========================

async def basic_transcribe():
    """
    Initializes the Amazon Transcribe client and manages the transcription session,
    including streaming audio and handling results.
    """
    client = TranscribeStreamingClient(region=AWS_REGION)
    stream = await client.start_stream_transcription(
        language_code=LANGUAGE_CODE,
        media_sample_rate_hz=SAMPLE_RATE_HZ,
        media_encoding=MEDIA_ENCODING,
    )
    handler = MyEventHandler(stream.output_stream)
    await asyncio.gather(write_chunks(stream), handler.handle_events())

# =========================
# Entry Point
# =========================

def main():
    """
    Sets up and starts the asynchronous event loop for the transcription process.
    Gracefully handles keyboard interruption.
    """
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(basic_transcribe())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == "__main__":
    main()
