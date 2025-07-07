document.getElementById('sendBtn').addEventListener('click', async function() {
    const audioInput = document.getElementById('audioInput');
    const status = document.getElementById('status');
    const audioPlayer = document.getElementById('audioPlayer');
    status.textContent = '';
    audioPlayer.style.display = 'none';
    if (!audioInput.files.length) {
        status.textContent = 'Please select a WAV file.';
        return;
    }
    const file = audioInput.files[0];
    if (file.type !== 'audio/wav') {
        status.textContent = 'Please upload a .wav file.';
        return;
    }
    status.textContent = 'Uploading and processing...';
    const formData = new FormData();
    formData.append('audio', file);
    try {
        // Use API_BASE_URL if set (for local dev)
        const apiUrl = (window.API_BASE_URL || '') + '/api/voice';
        const response = await fetch(apiUrl, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) {
            const err = await response.json();
            status.textContent = 'Error: ' + (err.error || response.statusText);
            return;
        }
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        audioPlayer.src = url;
        audioPlayer.style.display = 'block';
        status.textContent = 'Response ready!';
    } catch (e) {
        status.textContent = 'Network error.';
    }
});

// --- Add voice recording and live agent interaction ---
const recordBtn = document.getElementById('recordBtn');
const status = document.getElementById('status');
const audioPlayer = document.getElementById('audioPlayer');
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

recordBtn.addEventListener('click', async function() {
    if (!isRecording) {
        // Start recording
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            status.textContent = 'getUserMedia not supported in this browser.';
            return;
        }
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
            audioChunks = [];
            mediaRecorder.ondataavailable = e => {
                if (e.data.size > 0) audioChunks.push(e.data);
            };
            mediaRecorder.onstop = async () => {
                status.textContent = 'Processing your voice...';
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                // Convert to wav using browser API or send as webm and convert server-side
                const formData = new FormData();
                formData.append('audio', audioBlob, 'input.webm');
                // Optionally add a session_id for conversation continuity
                try {
                    const apiUrl = (window.API_BASE_URL || '') + '/api/voice';
                    const response = await fetch(apiUrl, {
                        method: 'POST',
                        body: formData
                    });
                    if (!response.ok) {
                        const err = await response.json();
                        status.textContent = 'Error: ' + (err.error || response.statusText);
                        return;
                    }
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    audioPlayer.src = url;
                    audioPlayer.style.display = 'block';
                    status.textContent = 'Agent response ready!';
                } catch (e) {
                    status.textContent = 'Network error.';
                }
            };
            mediaRecorder.start();
            isRecording = true;
            recordBtn.textContent = 'Stop Recording';
            status.textContent = 'Listening...';
        } catch (err) {
            status.textContent = 'Microphone access denied.';
        }
    } else {
        // Stop recording
        mediaRecorder.stop();
        isRecording = false;
        recordBtn.textContent = 'Start Talking';
    }
});
