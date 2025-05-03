# Real-Time Speech Transcription with Amazon Transcribe Streaming

This project demonstrates a real-time speech-to-text transcription pipeline using **Amazon Transcribe Streaming** and live microphone input in Python.

## Overview

The application captures audio from your microphone, streams it to Amazon Transcribe in real time, and prints both partial and final transcription results to the console.

## Features

* Real-time microphone audio capture
* Integration with AWS Transcribe Streaming
* Live transcription display with partial and complete results
* Asynchronous architecture using Python's `asyncio`
* Centralized configuration via code-level variables for easy customization

## Requirements

* Python 3.7+
* AWS credentials configured in your environment
* Microphone access

## Dependencies

Install required packages using pip:

```bash
pip install amazon-transcribe sounddevice numpy
```

> Ensure your Python environment includes the `amazon-transcribe` SDK, which provides native support for streaming transcriptions.

## Usage

To run the application, simply execute the script:

```bash
python aws_transcribe.py
```

The script captures audio from the default input device and begins transcription using Amazon Transcribe. Transcription results appear in the terminal.

### Supported Configuration

All key parameters are defined at the top of the script for convenience. You can easily modify the following variables to change runtime behavior:

* `AWS_REGION`: Region where Amazon Transcribe operates (e.g., `us-west-2`)
* `LANGUAGE_CODE`: Transcription language (e.g., `pt-BR`)
* `SAMPLE_RATE_HZ`: Audio sample rate in Hertz (e.g., `16000`)
* `MEDIA_ENCODING`: Audio encoding format (e.g., `pcm`)
* `CHANNELS`: Number of audio channels (must be `1` for mono)
* `DTYPE`: Data type of the audio buffer (e.g., `int16`)
* `CHUNK_SIZE`: Size of audio chunks to be read from the microphone

These settings make it simple to adapt the script to different audio configurations or AWS environments.

## Code Highlights

* Uses the `sounddevice` library to capture real-time audio.
* Implements a custom handler class inheriting from `TranscriptResultStreamHandler` to process transcription events.
* Runs concurrent coroutines to send audio chunks and receive transcription results simultaneously.
* Offers centralized variable definitions for region, language, format, and stream settings.

## Installation and Environment Setup

Follow these steps to set up the project in a clean and isolated environment using Python virtual environments:

### 1. Clone the Repository

```bash
git clone https://github.com/biagolini/PythonSpeakerDiarizationTool.git
cd PythonSpeakerDiarizationTool
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Project Dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Add Jupyter Support

If you intend to develop or test code using Jupyter Notebook, install the following packages to ensure compatibility with the virtual environment:

```bash
pip install notebook jupyterlab ipykernel
```

### 5. (Optional) Register the Virtual Environment with Jupyter

To make the virtual environment available as a kernel in Jupyter:

```bash
python -m ipykernel install --user --name=venv --display-name "Python (venv)"
```

### 6. (Optional) Verify Installed Packages

To list all installed packages within the virtual environment:

```bash
pip freeze
```


## Limitations and Credential Setup

While this project integrates smoothly with Amazon Transcribe Streaming, there are a few important considerations regarding AWS credential handling:

### Credential Injection

The script includes a section labeled `AWS Credential Injection`, which automatically retrieves AWS credentials using `boto3` and sets them as environment variables. This approach is particularly useful when working with [AWS SSO](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html) profiles, allowing you to leverage your existing authenticated CLI session without manually copying tokens.

This method supports:

* Automatic credential loading from an SSO profile (set via `AWS_PROFILE`)
* Dynamic export of `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` into the Python runtime environment

### Alternative Method: Manual Export

As an alternative to in-code injection, you may manually set environment variables before running the script:

```bash
export AWS_ACCESS_KEY_ID="xxxx"
export AWS_SECRET_ACCESS_KEY="xxxx"
export AWS_SESSION_TOKEN="xxxx"
```

This manual method is valid and compatible with the script, as the `amazon-transcribe` SDK relies on these environment variables if no credentials are passed programmatically.

### Limitation

The script uses the `amazon-transcribe` streaming SDK, which does **not** inherently support AWS SSO profiles. Therefore, without the credential injection logic (or manual export), using SSO-based authentication would fail unless valid credentials are available in environment variables.

The included credential injection logic is a convenient workaround to bridge that gap by leveraging `boto3`'s understanding of the AWS configuration ecosystem.

For users in AWS organizations utilizing SSO, this built-in logic simplifies integration without needing to manually fetch or export session tokens.


## Reference

For more information on getting started with Amazon Transcribe Streaming SDK, refer to the official AWS documentation:

[Amazon Transcribe SDK Getting Started Guide](https://docs.aws.amazon.com/transcribe/latest/dg/getting-started-sdk.html)

## License

This project is intended for educational and demonstration purposes. Adapt as needed for production use.

---

Feel free to customize this code to suit other languages, audio formats, or AWS regions.
