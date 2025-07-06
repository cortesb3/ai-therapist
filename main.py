import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
from stt import SpeechToText
from llm import LanguageModel
from tts import TextToSpeech

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'


def record_audio(filename, duration=None):
    print("Press Enter to start recording...")
    input()
    print("Recording... Press Enter to stop.")
    recording = []
    def callback(indata, frames, time, status):
        recording.append(indata.copy())
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE, callback=callback):
        input()  # Wait for Enter to stop
    audio = np.concatenate(recording, axis=0)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(np.dtype(DTYPE).itemsize)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())
    print(f"Saved recording to {filename}")


def play_audio_stream(audio_chunks, rate=22050):
    import pyaudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, 
    channels=1, rate=rate, output=True)
    header_skipped = False
    for chunk in audio_chunks:
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

    while True:
        print("\n--- New Interaction ---")
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            audio_path = tmp.name
        record_audio(audio_path)
        text = stt.transcribe(audio_path)
        print("You said:", text)
        os.remove(audio_path)

        if not text.strip():
            print("No speech detected. Try again.")
            continue

        response = llm.generate(text)
        print("LLM response:", response)

        print("Speaking response...")
        output_wav = "output.wav"
        tts.synthesize(response, output_path=output_wav)
        with open(output_wav, "rb") as f:
            wav_bytes = f.read()
        play_audio_stream([wav_bytes])
        print("Done speaking.")

        again = input("Press Enter for another round, or type 'q' to quit: ")
        if again.strip().lower() == 'q':
            break

if __name__ == "__main__":
    main()
