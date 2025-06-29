import requests

class TextToSpeech:
    def __init__(self, api_url="http://localhost:4123/v1/audio/speech/stream"):
        self.api_url = api_url

    def synthesize(self, text, output_path="output.wav"):
        # For compatibility: download full audio (not streaming)
        response = requests.post(self.api_url.replace("/stream", ""), json={"input": text})
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path

    def stream_synthesize(self, text, chunk_size=8192):
        """
        Stream audio chunks from the TTS API (for real-time playback or LiveKit integration).
        Yields bytes chunks as they arrive.
        """
        response = requests.post(
            self.api_url,
            json={"input": text, "streaming_strategy": "sentence", "streaming_chunk_size": 200},
            stream=True
        )
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                yield chunk
