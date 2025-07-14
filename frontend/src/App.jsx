import React, { useRef, useState } from 'react';

function App() {
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null); // For playback interruption

  const handleStart = async () => {
    setError('');
    setLoading(false);
    audioChunksRef.current = [];
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new window.MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };
      mediaRecorder.onstop = handleStop;
      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      setError('Microphone access denied.');
    }
  };

  const handleStop = async () => {
    setRecording(false);
    setLoading(true);
    // Stop any currently playing audio (interrupt TTS)
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    // Convert audio chunks to WAV using webm-to-wav workaround
    const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
    // Use browser's AudioContext to decode and re-encode as WAV
    try {
      const arrayBuffer = await audioBlob.arrayBuffer();
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
      const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
      // Convert to mono 16kHz WAV
      const wavBuffer = encodeWAV(audioBuffer, 16000);
      const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' });
      const formData = new FormData();
      formData.append('audio', wavBlob, 'input.wav');
      const res = await fetch('/api/voice', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json();
        setError(err.error || 'API error');
        setLoading(false);
        return;
      }
      const audioData = await res.blob();
      const url = URL.createObjectURL(audioData);
      const audio = new Audio(url);
      audioRef.current = audio;
      audio.play();
      setLoading(false);
    } catch (e) {
      setError('Failed to contact backend or convert audio.');
      setLoading(false);
    }
  };

  // Helper to encode AudioBuffer to mono 16kHz WAV
  function encodeWAV(audioBuffer, targetSampleRate = 16000) {
    // Downsample to 16kHz mono
    const numChannels = 1;
    const input = audioBuffer.getChannelData(0);
    const sampleRate = audioBuffer.sampleRate;
    const ratio = sampleRate / targetSampleRate;
    const length = Math.floor(input.length / ratio);
    const result = new Float32Array(length);
    for (let i = 0; i < length; i++) {
      result[i] = input[Math.floor(i * ratio)];
    }
    // Convert to 16-bit PCM
    const buffer = new ArrayBuffer(44 + length * 2);
    const view = new DataView(buffer);
    // RIFF identifier 'RIFF'
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + length * 2, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true); // Subchunk1Size
    view.setUint16(20, 1, true); // AudioFormat (PCM)
    view.setUint16(22, numChannels, true);
    view.setUint32(24, targetSampleRate, true);
    view.setUint32(28, targetSampleRate * numChannels * 2, true); // ByteRate
    view.setUint16(32, numChannels * 2, true); // BlockAlign
    view.setUint16(34, 16, true); // BitsPerSample
    writeString(view, 36, 'data');
    view.setUint32(40, length * 2, true);
    // Write PCM samples
    let offset = 44;
    for (let i = 0; i < length; i++, offset += 2) {
      let s = Math.max(-1, Math.min(1, result[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
    return buffer;
  }

  function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }

  const handleButton = () => {
    // Interrupt TTS playback if user presses button
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    if (!recording) {
      handleStart();
    } else {
      mediaRecorderRef.current && mediaRecorderRef.current.stop();
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: 80 }}>
      <h1>AI Voice Therapist</h1>
      <button
        style={{
          width: 120,
          height: 120,
          borderRadius: '50%',
          background: recording ? '#e74c3c' : '#2ecc71',
          color: 'white',
          fontSize: 24,
          border: 'none',
          margin: 20,
          boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
          cursor: 'pointer',
        }}
        onMouseDown={handleButton}
        onMouseUp={handleButton}
        onTouchStart={handleButton}
        onTouchEnd={handleButton}
        disabled={loading}
      >
        {recording ? 'Release to Send' : 'Push to Talk'}
      </button>
      {loading && <p>Processing...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <p style={{ color: '#888', marginTop: 40 }}>Hold the button, speak, and release to talk to Ava.</p>
    </div>
  );
}

export default App;
