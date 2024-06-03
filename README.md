# Transcriber Microservice

This microservice provides endpoints for transcribing audio and video files using the Whisper API.

## Features

- Transcribe audio and video files.
- Supports multiple file formats: MP3, WAV, M4A, MP4, FLAC.
- Uses FastAPI for handling requests.

## Requirements

- Docker

## Installation

1. **Clone the repository:**
2. **git clone <repository-url>**
3. **cd <repository-directory>**
4. **Set up environment variables: Create a `.env` file with the following content:**
GPT_API_KEY=your_api_key_here
BASE_DIR=/app
5. **Build and run the Docker container:**
docker-compose up --build

## Usage

### Transcribe a File

Send a POST request to the `/transcribe/` endpoint with the file to transcribe.

### Example using `requests` in Python

```python
import requests

file_path = 'path/to/your/file.mp4'

files = {'file': open(file_path, 'rb')}
response = requests.post('http://localhost:4004/transcribe/', files=files)
print(response.json())
