from pywhispercpp.model import Model

class SpeechToText:
    def __init__(self, model_name='base.en'):
        self.model = Model(model_name)

    def transcribe(self, audio_path):
        segments = self.model.transcribe(audio_path)
        return ' '.join(segment.text for segment in segments)
