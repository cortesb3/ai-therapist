# ai-therapist

A modular, fully local pipeline for live voice interaction using:
- **STT:** pywhispercpp
- **LLM:** Ollama
- **TTS:** Coqui TTS (local, open-source)

## Requirements
- Python 3.10 or 3.11 (recommended for Coqui TTS compatibility)
- [Ollama](https://github.com/ollama/ollama) running locally with your model (e.g. `llama3.2:latest`)
- ffmpeg (for audio conversion)
- pyaudio (for real-time playback)


## Setup

1. **Install uv (Python package/dependency manager):**
   ```sh
   brew install uv
   ```

2. **Install Python dependencies:**
   ```sh
   cd ai-therapist
   uv sync
   ```

3. **Install ffmpeg (macOS):**
   ```sh
   brew install ffmpeg
   ```

4. **Pull your LLM model with Ollama:**
   ```sh
   ollama pull llama3.2:latest
   # or any other model you want
   ```


## Running the Backend API Server

1. Make sure Ollama is running and your model is pulled.
2. In the `ai-therapist` directory, run:
   ```sh
   uv run api_server.py
   ```
   This will start the backend server at http://localhost:5000

## Running the Frontend

1. In a new terminal, go to the `frontend` directory:
   ```sh
   cd frontend
   npm install
   npm run dev
   ```
   The app will be available at http://localhost:5173 and will proxy API requests to your backend.

---

---

## Troubleshooting
- **TTS install errors:** Use Python 3.10 or 3.11, install numpy/scipy first, then TTS.
- **STT error:** Ensure your input WAV is 16kHz mono.
- **LLM error:** Make sure the model is pulled in Ollama and the name matches.
- **Audio not playing:** Install `pyaudio`.

---

For more details, see:
- [Coqui TTS Docs](https://docs.coqui.ai/en/latest/)
- [Ollama](https://github.com/ollama/ollama)
- [pywhispercpp](https://pypi.org/project/pywhispercpp/)
