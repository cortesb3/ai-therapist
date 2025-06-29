from stt import SpeechToText
from llm import LanguageModel
from tts import TextToSpeech

# Optional: for real-time playback (local testing)
try:
    import pyaudio
except ImportError:
    pyaudio = None

def play_audio_stream(audio_chunks, rate=22050):
    """Play audio chunks in real time using PyAudio (WAV, 16-bit PCM, mono)."""
    if not pyaudio:
        print("PyAudio not installed. Install with 'pip install pyaudio' for real-time playback.")
        return
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, output=True)
    header_skipped = False
    for chunk in audio_chunks:
        # Skip WAV header (44 bytes) on first chunk
        if not header_skipped and len(chunk) > 44:
            chunk = chunk[44:]
            header_skipped = True
        stream.write(chunk)
    stream.stop_stream()
    stream.close()
    p.terminate()

def main():
    stt = SpeechToText()
    llm = LanguageModel()
    tts = TextToSpeech()

    # Use default audio file if available
    default_audio_path = "computer_mail_waiting_16k.wav"
    print(f"Press Enter to use the default audio file: {default_audio_path}")
    audio_path = input("Audio file path: ").strip()
    if not audio_path:
        audio_path = default_audio_path
    text = stt.transcribe(audio_path)
    print("You said:", text)

    response = llm.generate(text)
    print("LLM response:", response)

    # --- Streaming TTS Example ---
    print("Speaking response (streaming)...")
    audio_chunks = tts.stream_synthesize(response)
    play_audio_stream(audio_chunks)
    print("Done speaking.")

    # --- File-based fallback ---
    # tts.synthesize(response)
    # print("Response spoken and saved to output.wav")

    # TODO: Replace audio input/output with LiveKit/WebRTC streams for full-duplex, interruptible UX
    # - Receive audio from LiveKit, transcribe in real time
    # - On user interruption, stop TTS playback and restart loop
    # - Send TTS audio chunks to LiveKit for playback

if __name__ == "__main__":
    main()
