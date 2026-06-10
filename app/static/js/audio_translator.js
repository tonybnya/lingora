// Lingora Audio Translator — mic capture, WebSocket streaming, live translation
// Uses Gemini Live API via backend WebSocket for real-time audio-to-text translation.

(function () {
    'use strict';

    // -----------------------------------------------------------------------
    //  State
    // -----------------------------------------------------------------------
    let ws = null;
    let audioCtx = null;
    let processor = null;
    let micSource = null;
    let mediaStream = null;
    let recording = false;
    let reconnectTimer = null;

    const RECONNECT_DELAY_MS = 2000;

    // -----------------------------------------------------------------------
    //  DOM refs
    // -----------------------------------------------------------------------
    const btn = document.getElementById('audio-record-btn');
    const langInput = document.getElementById('audio-language');
    const statusDot = document.getElementById('audio-status-dot');
    const statusText = document.getElementById('audio-status-text');
    const resultsEl = document.getElementById('audio-transcriptions');

    // -----------------------------------------------------------------------
    //  Re-use translator.js helpers via window globals
    // -----------------------------------------------------------------------
    const notify = window.notify || function (o) {
        console.log('[notify]', o.type, o.title, o.message);
    };
    const escapeHtml = window.escapeHtml || function (s) {
        if (s == null) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    };

    // -----------------------------------------------------------------------
    //  PCM helpers
    // -----------------------------------------------------------------------
    function float32ToInt16(float32) {
        const len = float32.length;
        const i16 = new Int16Array(len);
        for (let i = 0; i < len; i++) {
            const s = Math.max(-1, Math.min(1, float32[i]));
            i16[i] = s < 0 ? s * 32768 : s * 32767;
        }
        return i16;
    }

    function resampleTo16kHz(audioData, fromRate) {
        if (fromRate === 16000) return audioData;
        const ratio = fromRate / 16000;
        const newLen = Math.round(audioData.length / ratio);
        const out = new Float32Array(newLen);
        for (let i = 0; i < newLen; i++) {
            const pos = i * ratio;
            const idx = Math.floor(pos);
            const frac = pos - idx;
            const i0 = Math.min(idx, audioData.length - 1);
            const i1 = Math.min(idx + 1, audioData.length - 1);
            out[i] = audioData[i0] + (audioData[i1] - audioData[i0]) * frac;
        }
        return out;
    }

    // -----------------------------------------------------------------------
    //  Set connection status
    // -----------------------------------------------------------------------
    function setStatus(connected) {
        if (statusDot) {
            statusDot.className = 'audio-status-dot' + (connected ? ' connected' : '');
        }
        if (statusText) {
            statusText.textContent = connected ? 'Connected' : 'Disconnected';
        }
    }

    // -----------------------------------------------------------------------
    //  Append a translation result to the list
    // -----------------------------------------------------------------------
    function appendResult(source, translation) {
        if (!resultsEl) return;
        const el = document.createElement('div');
        el.className = 'audio-transcription-item';
        el.innerHTML =
            '<div class="audio-source-text">' + escapeHtml(source) + '</div>' +
            '<div class="audio-translated-text">' + escapeHtml(translation) + '</div>';
        resultsEl.prepend(el);
    }

    // -----------------------------------------------------------------------
    //  Clean up mic + context
    // -----------------------------------------------------------------------
    function teardownMic() {
        if (processor && micSource) {
            processor.disconnect();
            micSource.disconnect();
        }
        if (audioCtx) {
            audioCtx.close().catch(function () {});
        }
        if (mediaStream) {
            mediaStream.getTracks().forEach(function (t) { t.stop(); });
        }
        processor = null;
        micSource = null;
        audioCtx = null;
        mediaStream = null;
    }

    // -----------------------------------------------------------------------
    //  Stop recording
    // -----------------------------------------------------------------------
    function stopRecording() {
        recording = false;
        if (ws) {
            ws.close();
            ws = null;
        }
        teardownMic();
        setStatus(false);
        if (btn) {
            btn.textContent = 'Start Recording';
            btn.classList.remove('recording');
        }
        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
        }
    }

    // -----------------------------------------------------------------------
    //  Start recording
    // -----------------------------------------------------------------------
    function startRecording() {
        var language = langInput ? langInput.value.trim() : '';
        if (!language) {
            notify({ type: 'error', title: 'Missing language', message: 'Enter a target language.' });
            return;
        }

        // WebSocket
        var protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
        ws = new WebSocket(protocol + '//' + location.host + '/ws/audio-translate');

        ws.onopen = function () {
            // Send config
            ws.send(JSON.stringify({ language: language }));

            // Start microphone
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(function (stream) {
                    mediaStream = stream;

                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    var sampleRate = audioCtx.sampleRate;
                    micSource = audioCtx.createMediaStreamSource(stream);

                    var bufferSize = 4096;
                    processor = audioCtx.createScriptProcessor(bufferSize, 1, 1);

                    processor.onaudioprocess = function (e) {
                        if (!ws || ws.readyState !== WebSocket.OPEN) return;
                        var input = e.inputBuffer.getChannelData(0);
                        var resampled = resampleTo16kHz(input, sampleRate);
                        var pcm = float32ToInt16(resampled);
                        ws.send(pcm.buffer);
                    };

                    micSource.connect(processor);
                    processor.connect(audioCtx.destination);

                    recording = true;
                    setStatus(true);
                    if (btn) {
                        btn.textContent = 'Stop Recording';
                        btn.classList.add('recording');
                    }
                })
                .catch(function (err) {
                    notify({ type: 'error', title: 'Mic access denied', message: err.message });
                    if (ws) { ws.close(); ws = null; }
                    setStatus(false);
                });
        };

        ws.onmessage = function (e) {
            var data;
            try { data = JSON.parse(e.data); } catch (_) { return; }

            if (data.type === 'translation') {
                appendResult(data.source, data.translation);
            } else if (data.type === 'error') {
                notify({ type: 'error', title: 'Translation error', message: data.message });
            }
        };

        ws.onerror = function () {
            notify({ type: 'error', title: 'WebSocket error', message: 'Connection lost.' });
            stopRecording();
        };

        ws.onclose = function () {
            if (recording) {
                // Unexpected close – try to reconnect
                notify({ type: 'info', title: 'Disconnected', message: 'Reconnecting in ' + (RECONNECT_DELAY_MS / 1000) + 's…' });
                teardownMic();
                setStatus(false);
                reconnectTimer = setTimeout(startRecording, RECONNECT_DELAY_MS);
            }
        };
    }

    // -----------------------------------------------------------------------
    //  Toggle recording
    // -----------------------------------------------------------------------
    window.toggleAudioRecording = function () {
        if (recording) {
            stopRecording();
        } else {
            startRecording();
        }
    };

    // Expose helpers for other modules
    window.audioTranslatorStop = stopRecording;
})();
