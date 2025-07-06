from TTS.api import TTS
import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile
import io
import threading
import time

class TextToSpeech:
    def __init__(self, model_name="tts_models/en/ljspeech/fast_pitch"):
        self.tts = TTS(model_name)

    def synthesize(self, text):
        # Synthesize speech and return as bytes (do not save to disk)
        wav = self.tts.tts(text=text)
        wav = np.array(wav)
        wav_int16 = np.int16(wav / np.max(np.abs(wav)) * 32767)
        buf = io.BytesIO()
        scipy.io.wavfile.write(buf, self.tts.synthesizer.output_sample_rate, wav_int16)
        buf.seek(0)
        return buf.read()

    def play(self, text):
        # Synthesize and play audio directly
        wav = self.tts.tts(text=text)
        wav = np.array(wav)
        sd.play(wav, self.tts.synthesizer.output_sample_rate)
        sd.wait()

    def synthesize_stream(self, text, chunk_size=2048):
        # Synthesize speech and yield audio chunks for streaming playback
        wav = self.tts.tts(text=text)
        wav = np.array(wav)
        wav_int16 = np.int16(wav / np.max(np.abs(wav)) * 32767)
        buf = io.BytesIO()
        scipy.io.wavfile.write(buf, self.tts.synthesizer.output_sample_rate, wav_int16)
        buf.seek(0)
        # Skip WAV header (44 bytes)
        buf.read(44)
        while True:
            chunk = buf.read(chunk_size)
            if not chunk:
                break
            yield chunk

    def play_stream(self, text, stop_event=None, chunk_size=2048):
        # Synthesize speech and play audio in a streaming, smooth way
        wav = self.tts.tts(text=text)
        wav = np.array(wav)
        wav_int16 = np.int16(wav / np.max(np.abs(wav)) * 32767)
        # Play the whole audio, but allow interruption
        def playback():
            try:
                sd.play(wav_int16, self.tts.synthesizer.output_sample_rate)
                sd.wait()
            except Exception as e:
                print(f"Playback error: {e}")
        t = threading.Thread(target=playback)
        t.start()
        try:
            while t.is_alive():
                if stop_event and stop_event.is_set():
                    sd.stop()
                    break
                time.sleep(0.05)
        finally:
            t.join()
