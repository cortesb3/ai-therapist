import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
import signal
from stt import SpeechToText
from llm import LanguageModel
from tts import TextToSpeech

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'

# Graceful exit on Ctrl+C
import sys
def signal_handler(sig, frame):
    print("\nExiting...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def record_audio(filename, duration=None):
    print("Recording... Press any key or Ctrl+C to stop.")
    import sys
    import termios
    import tty
    import threading
    recording = []
    stop = threading.Event()
    def callback(indata, frames, time, status):
        recording.append(indata.copy())
        if stop.is_set():
            raise sd.CallbackStop()
    def key_listener():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            sys.stdin.read(1)
            stop.set()
        except KeyboardInterrupt:
            stop.set()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    listener_thread = threading.Thread(target=key_listener)
    listener_thread.start()
    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE, callback=callback):
            while not stop.is_set():
                sd.sleep(100)
    except KeyboardInterrupt:
        print("\nRecording interrupted.")
        stop.set()
    audio = np.concatenate(recording, axis=0) if recording else np.zeros((0, CHANNELS), dtype=DTYPE)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(np.dtype(DTYPE).itemsize)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())
    print(f"Saved recording to {filename}")
    listener_thread.join()


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
        record_audio(audio_path)
        text = stt.transcribe(audio_path)
        print("You said:", text)
        os.remove(audio_path)

        if not text.strip():
            print("No speech detected. Try again.")
            continue

        response = llm.generate(text)
        print("LLM response:", response)

        print("Speaking response... (Press any key to interrupt)")
        import threading
        import sys
        import termios
        import tty
        stop_playback = threading.Event()
        def playback():
            try:
                tts.play_stream(response, stop_event=stop_playback)
            except Exception as e:
                print(f"Playback error: {e}")
        t = threading.Thread(target=playback)
        t.start()
        # Set terminal to raw mode to capture any key
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)  # Wait for any key
            if key == '\r' or key == '\n':
                print("Interrupting playback with Enter. Returning to recording...")
                stop_playback.set()
                t.join()
                continue  # Go back to recording automatically
            else:
                print("Interrupting playback with other key.")
                stop_playback.set()
        except KeyboardInterrupt:
            print("\nExiting...")
            stop_playback.set()
            t.join()
            break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        t.join()
        print("Done speaking.")

        again = input("Press Enter for another round, or type 'q' to quit: ")
        if again.strip().lower() == 'q':
            break

if __name__ == "__main__":
    main()
