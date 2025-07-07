from flask import Flask, request, send_file, jsonify
import tempfile
import os
import traceback
from stt import SpeechToText
from llm import LanguageModel
from tts import TextToSpeech

app = Flask(__name__)
stt = SpeechToText()
llm = LanguageModel()
tts = TextToSpeech()

@app.route('/api/voice', methods=['POST'])
def voice_interaction():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    audio_file = request.files['audio']
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        audio_path = tmp.name
        audio_file.save(audio_path)
    try:
        text = stt.transcribe(audio_path)
        print(f"[DEBUG] Transcribed text: {text}")
        if not text.strip():
            os.remove(audio_path)
            return jsonify({'error': 'No speech detected'}), 400
        response = llm.generate(text)
        print(f"[DEBUG] LLM response: {response}")
        tts_wav_bytes = tts.synthesize(response)
        print(f"[DEBUG] TTS wav bytes length: {len(tts_wav_bytes)}")
        if not tts_wav_bytes or len(tts_wav_bytes) < 44:  # 44 bytes is the minimum WAV header size
            return jsonify({'error': 'TTS output is empty or invalid'}), 500
        # Save TTS output to temp file for sending
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tts_tmp:
            tts_tmp.write(tts_wav_bytes)
            tts_tmp.flush()
            tts_path = tts_tmp.name
        os.remove(audio_path)
        return send_file(tts_path, mimetype='audio/wav', as_attachment=True, download_name='response.wav')
    except Exception as e:
        print("[ERROR] Exception occurred:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if 'tts_path' in locals() and os.path.exists(tts_path):
            os.remove(tts_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
