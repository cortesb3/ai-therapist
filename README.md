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

1. **Install Python dependencies:**
   ```sh
   cd ai-therapist
   pip install -r requirements.txt
   # or, if using uv:
   uv pip install -r requirements.txt
   ```

2. **Install ffmpeg (macOS):**
   ```sh
   brew install ffmpeg
   ```

3. **Install pyaudio (for playback):**
   ```sh
   pip install pyaudio
   # or
   uv pip install pyaudio
   ```

4. **Install Coqui TTS (for TTS):**
   - Coqui TTS supports Python 3.10 and 3.11. If you have Python 3.12+, create a Python 3.10 or 3.11 virtual environment.
   - Then run:
   ```sh
   pip install TTS
   # or
   uv pip install TTS
   ```
   - If you get numpy/scipy build errors, install them first:
   ```sh
   pip install numpy scipy
   # or
   uv pip install numpy scipy
   ```

5. **Pull your LLM model with Ollama:**
   ```sh
   ollama pull llama3.2:latest
   # or any other model you want
   ```

## Running the Live Voice Agent

1. Make sure Ollama is running and your model is pulled.
2. In the `ai-therapist` directory, run:
   ```sh
   python main.py
   ```
3. Follow the prompts to record, transcribe, and interact live.

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
