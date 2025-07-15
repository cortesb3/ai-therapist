import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
import signal
from stt import SpeechToText
from llm import LanguageModel
from tts import TextToSpeech
import webrtcvad
import time

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'

# Graceful exit on Ctrl+C
import sys
def signal_handler(sig, frame):
    print("\nExiting...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def record_audio_vad(filename, aggressiveness=2, max_record_time=30, silence_timeout=1.0):
    print("Listening... (speak to start, stop talking to end)")
    vad = webrtcvad.Vad(aggressiveness)

    sample_rate = SAMPLE_RATE
    frame_duration = 30  # ms
    frame_size = int(sample_rate * frame_duration / 1000)
    buffer = []
    silence_start = None
    started = False
    start_time = time.time()

    def is_speech(frame_bytes):
        return vad.is_speech(frame_bytes, sample_rate)

    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16') as stream:
        while True:
            frame, _ = stream.read(frame_size)
            frame_bytes = frame.tobytes()
            if is_speech(frame_bytes):
                buffer.append(frame)
                if not started:
                    started = True
                    print("Speech detected, recording...")
                silence_start = None
            else:
                if started:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > silence_timeout:
                        print("Silence detected, stopping recording.")
                        break
            if started and (time.time() - start_time > max_record_time):
                print("Max record time reached, stopping.")
                break
    if buffer:
        audio = np.concatenate(buffer, axis=0)
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(np.dtype('int16').itemsize)
            wf.setframerate(sample_rate)
            wf.writeframes(audio.tobytes())
        print(f"Saved recording to {filename}")
    else:
        print("No speech detected.")
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(np.dtype('int16').itemsize)
            wf.setframerate(sample_rate)
            wf.writeframes(b"")


def play_audio_stream(audio_chunks, rate=22050, stop_event=None):
    import pyaudio
    import select
    import sys
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, 
    channels=1, rate=rate, output=True)
    header_skipped = False
    try:
        for chunk in audio_chunks:
            if stop_event and stop_event.is_set():
                print("Playback interrupted by user.")
                break
            if not header_skipped and len(chunk) > 44:
                chunk = chunk[44:]
                header_skipped = True
            stream.write(chunk)
    except KeyboardInterrupt:
        print("\nPlayback interrupted.")
    finally:
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
        record_audio_vad(audio_path)
        text = stt.transcribe(audio_path)
        print("You said:", text)
        os.remove(audio_path)

        if not text.strip():
            print("No speech detected. Try again.")
            continue

        response = llm.generate(text)
        print("LLM response:", response)

        print("Speaking response... (Press Enter to interrupt)")
        import threading
        import sys
        import termios
        import tty
        import select
        stop_playback = threading.Event()
        def playback():
            try:
                tts.play_stream(response, stop_event=stop_playback)
            except Exception as e:
                print(f"Playback error: {e}")
        t = threading.Thread(target=playback)
        t.start()
        # Set terminal to raw mode to capture Enter key
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            print("(Press Enter to interrupt and record, Ctrl+C to exit)")
            while t.is_alive():
                dr, _, _ = select.select([sys.stdin], [], [], 0.05)
                if dr:
                    key = sys.stdin.read(1)
                    if key == '\x03':  # Ctrl+C
                        print("\nExiting...")
                        stop_playback.set()
                        t.join()
                        sys.exit(0)
                    if key == '\r' or key == '\n':
                        print("Interrupting playback with Enter. Returning to recording...")
                        stop_playback.set()
                        break
                if stop_playback.is_set():
                    break
        except KeyboardInterrupt:
            print("\nExiting...")
            stop_playback.set()
            t.join()
            sys.exit(0)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        t.join()
        print("Done speaking.")
        # Immediately loop back to next recording, no input() prompt

if __name__ == "__main__":
    main()
