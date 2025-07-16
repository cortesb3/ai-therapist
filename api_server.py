from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import tempfile
import os
import traceback
from stt import SpeechToText
from llm import LanguageModel
from tts import TextToSpeech

app = Flask(__name__)
CORS(app)
stt = SpeechToText()
llm = LanguageModel()
tts = TextToSpeech()

# Maintain conversation state per session
sessions = {}

def get_llm_for_session(session_id):
    if session_id not in sessions:
        sessions[session_id] = LanguageModel()
    return sessions[session_id]

@app.route('/api/voice', methods=['POST'])
def voice_interaction():
    # Check for greeting param (either form or query string)
    greeting = request.form.get('greeting') or request.args.get('greeting')
    if greeting:
        try:
            greeting_text = "Hello! How can I help you today?"
            tts_wav_bytes = tts.synthesize(greeting_text)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tts_tmp:
                tts_tmp.write(tts_wav_bytes)
                tts_tmp.flush()
                tts_path = tts_tmp.name
            return send_file(tts_path, mimetype='audio/wav', as_attachment=True, download_name='greeting.wav')
        except Exception as e:
            print("[ERROR] Exception in greeting:")
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
        finally:
            if 'tts_path' in locals() and os.path.exists(tts_path):
                os.remove(tts_path)

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

@app.route('/api/live-voice', methods=['POST'])
def live_voice_interaction():
    session_id = request.form.get('session_id')
    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400
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
        llm = get_llm_for_session(session_id)
        response = llm.generate(text)
        print(f"[DEBUG] LLM response: {response}")
        tts_wav_bytes = tts.synthesize(response)
        print(f"[DEBUG] TTS wav bytes length: {len(tts_wav_bytes)}")
        if not tts_wav_bytes or len(tts_wav_bytes) < 44:
            return jsonify({'error': 'TTS output is empty or invalid'}), 500
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
