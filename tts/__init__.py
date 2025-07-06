from TTS.api import TTS
import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile

class TextToSpeech:
    def __init__(self, model_name="tts_models/en/ljspeech/tacotron2-DDC"):
        self.tts = TTS(model_name)

    def synthesize(self, text, output_path="output.wav"):
        # Synthesize speech and save to WAV file
        wav = self.tts.tts(text=text)
        # Normalize and save as 16-bit PCM WAV
        wav = np.array(wav)
        wav_int16 = np.int16(wav / np.max(np.abs(wav)) * 32767)
        scipy.io.wavfile.write(output_path, self.tts.synthesizer.output_sample_rate, wav_int16)
        return output_path

    def play(self, text):
        # Synthesize and play audio directly
        wav = self.tts.tts(text=text)
        wav = np.array(wav)
        sd.play(wav, self.tts.synthesizer.output_sample_rate)
        sd.wait()
