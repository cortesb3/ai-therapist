# ai-therapist

A modular pipeline for live or file-based voice interaction using STT (pywhispercpp), LLM (Ollama), and TTS (Chatterbox TTS API).

## Requirements

- Python 3.10+
- [Ollama](https://github.com/ollama/ollama) running locally with the desired model pulled (e.g. `llama3.2:latest`)
- [Chatterbox TTS API](https://github.com/travisvn/chatterbox-tts-api) running (see below)
- ffmpeg (for audio conversion)
- pyaudio (for real-time playback, optional)

## Setup

1. **Install Python dependencies:**
   ```sh
   cd ai-therapist
   pip install -r requirements.txt
   ```

2. **Install ffmpeg (for macOS):**
   ```sh
   brew install ffmpeg
   ```

3. **Install pyaudio (optional, for real-time playback):**
   ```sh
   pip install pyaudio
   ```

4. **Pull the LLM model with Ollama:**
   ```sh
   ollama pull llama3.2:latest
   # or whatever model you want to use
   ```

5. **Convert your audio file to 16kHz mono WAV:**
   ```sh
   ffmpeg -i input.wav -ar 16000 -ac 1 input_16k.wav
   ```

6. **Start Chatterbox TTS API:**
   ```sh
   cd ../chatterbox-tts-api
   docker compose -f docker/docker-compose.yml up -d --build
   # Wait for http://localhost:4123/health to show status: healthy
   ```

## Running the Pipeline

1. Make sure Ollama and Chatterbox TTS API are running and healthy.
2. In the `ai-therapist` directory, run:
   ```sh
   python main.py
   ```
3. Press Enter to use the default audio file (e.g. `computer_mail_waiting_16k.wav`), or enter a path to another 16kHz mono WAV file.
4. You will see the transcript, LLM response, and (if pyaudio is installed) hear the TTS output.

## requirements.txt

```
pywhispercpp
ollama-python
requests
pyaudio  # optional, for real-time playback
```

---

# chatterbox-tts-api

## Requirements
- Docker (recommended)
- CPU or GPU (GPU recommended for faster TTS)

## Setup & Run

1. **Build and start the API:**
   ```sh
   cd chatterbox-tts-api
   docker compose -f docker/docker-compose.yml up -d --build
   ```
2. **Wait for the API to be healthy:**
   - Check [http://localhost:4123/health](http://localhost:4123/health) for `"status":"healthy"`.

## requirements.txt (for Docker build)

```
fastapi
uvicorn[standard]
python-dotenv
python-multipart
requests
psutil
chatterbox-tts
torch==2.5.1
torchaudio==2.5.1
```

---

## Troubleshooting
- **STT error:** Ensure your input WAV is 16kHz mono.
- **LLM error:** Make sure the model is pulled in Ollama and the name matches.
- **TTS stuck:** Wait for Chatterbox TTS API to finish initializing (can take several minutes on first run).
- **Audio not playing:** Install `pyaudio`.

---

For more details, see the respective project READMEs:
- [Chatterbox TTS API](../chatterbox-tts-api/README.md)
- [Ollama Python](https://github.com/ollama/ollama-python)
- [pywhispercpp](https://pypi.org/project/pywhispercpp/)
