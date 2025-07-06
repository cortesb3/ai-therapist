from TTS.api import TTS
import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile
import io

class TextToSpeech:
    def __init__(self, model_name="tts_models/en/ljspeech/tacotron2-DDC"):
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
