// Lingora Translator — async submit with axios, validation, progress bar, notifications
// Uses HelixDot-inspired progress bar that fills as the backend processes the request.

(function () {
    'use strict';

    // Footer year
    const yearEl = document.getElementById('footer-year');
    if (yearEl) yearEl.textContent = new Date().getFullYear();

    // -----------------------------------------------------------------------
    //  Custom notification system (DESIGN.md styled)
    // -----------------------------------------------------------------------
    function notify({ type = 'info', title = '', message = '', duration = 4500 }) {
        const container = document.getElementById('notify-container');
        if (!container) return;

        const el = document.createElement('div');
        el.className = `notify notify-${type}`;
        el.innerHTML = `
            <div class="notify-icon"></div>
            <div class="notify-body">
                ${title ? `<div class="notify-title">${title}</div>` : ''}
                <div class="notify-message">${message}</div>
            </div>
            <button class="notify-close" aria-label="Close">&times;</button>
        `;
        container.appendChild(el);

        // Animate in
        requestAnimationFrame(() => el.classList.add('visible'));

        const close = () => {
            el.classList.remove('visible');
            setTimeout(() => el.remove(), 300);
        };
        el.querySelector('.notify-close').addEventListener('click', close);
        if (duration > 0) setTimeout(close, duration);
    }

    // -----------------------------------------------------------------------
    //  HelixDot-inspired progress bar
    //  We use a row of dots that fill in sequence as the request advances.
    // -----------------------------------------------------------------------
    const HelixProgress = (() => {
        const DOTS = 24;

        function create(container) {
            container.classList.add('helix-progress');
            container.innerHTML = '';

            const track = document.createElement('div');
            track.className = 'helix-progress-track';

            const fill = document.createElement('div');
            fill.className = 'helix-progress-fill';

            const label = document.createElement('div');
            label.className = 'helix-progress-label';
            label.textContent = '0%';

            container.appendChild(track);
            container.appendChild(fill);
            container.appendChild(label);

            // Build dots
            for (let i = 0; i < DOTS; i++) {
                const dot = document.createElement('div');
                dot.className = 'helix-progress-dot';
                track.appendChild(dot);
            }

            return {
                set(pct) {
                    pct = Math.max(0, Math.min(100, pct));
                    fill.style.width = `${pct}%`;
                    label.textContent = `${Math.floor(pct)}%`;

                    const dots = track.children;
                    const active = Math.floor((pct / 100) * DOTS);
                    for (let i = 0; i < DOTS; i++) {
                        if (i < active) dots[i].classList.add('active');
                        else dots[i].classList.remove('active');
                    }
                },
                reset() {
                    fill.style.width = '0%';
                    label.textContent = '0%';
                    const dots = track.children;
                    for (let i = 0; i < DOTS; i++) {
                        dots[i].classList.remove('active');
                    }
                },
            };
        }

        return { create };
    })();

    // -----------------------------------------------------------------------
    //  Validation
    // -----------------------------------------------------------------------
    function validate(text, languagesRaw) {
        const errors = [];
        if (!text || !text.trim()) errors.push('Please enter the text you want to translate.');

        const langs = (languagesRaw || '')
            .split(',')
            .map((l) => l.trim())
            .filter(Boolean);

        if (langs.length === 0) {
            errors.push('Please specify at least one target language.');
        }

        return { valid: errors.length === 0, errors, languages: langs };
    }

    // -----------------------------------------------------------------------
    //  submitTranslation — async, axios, progress synced with backend
    // -----------------------------------------------------------------------
    window.submitTranslation = async function () {
        const textEl = document.getElementById('input-text');
        const langEl = document.getElementById('languages');
        const btn = document.getElementById('translate-btn');
        const progressContainer = document.getElementById('progress-container');
        const resultsArea = document.getElementById('results');
        const taskIdEl = document.getElementById('task-id');

        const text = textEl.value;
        const languagesRaw = langEl.value;

        const { valid, errors, languages } = validate(text, languagesRaw);
        if (!valid) {
            notify({
                type: 'error',
                title: 'Invalid input',
                message: errors.join(' '),
            });
            return;
        }

        // Reset UI
        resultsArea.classList.remove('visible');
        progressContainer.classList.add('visible');
        if (taskIdEl) taskIdEl.textContent = '';
        btn.disabled = true;
        btn.innerHTML = '<span class="btn-spinner"></span> Submitting…';

        const progress = HelixProgress.create(progressContainer);
        progress.set(0);

        // -------------------------------------------------------------------
        //  Step 1 — POST /translate to create the task
        // -------------------------------------------------------------------
        let taskId;
        try {
            const { data } = await axios.post('/translate', {
                text: text.trim(),
                languages: languages.join(', '),
            });

            taskId = data.id;
            if (taskIdEl) taskIdEl.textContent = `#${taskId}`;

            notify({
                type: 'success',
                title: 'Request received',
                message: `Task #${taskId} is being processed.`,
            });

            // Optimistic UI bump after task is accepted
            progress.set(15);
        } catch (err) {
            console.error(err);
            notify({
                type: 'error',
                title: 'Submission failed',
                message: err.response?.data?.detail || err.message || 'Unknown error',
            });
            progressContainer.classList.remove('visible');
            btn.disabled = false;
            btn.innerHTML = 'Translate';
            return;
        }

        btn.innerHTML = '<span class="btn-spinner"></span> Translating…';

        // -------------------------------------------------------------------
        //  Step 2 — Poll /translate/{id} until status === 'completed'
        //  We tick the progress bar between polls. As soon as the response
        //  contains a list of partial translations, we count them and
        //  advance the bar proportionally.
        // -------------------------------------------------------------------
        const POLL_INTERVAL_MS = 1500;
        const expectedLanguages = languages.length;

        // Smooth progress animation between polls
        let displayed = 15;
        let target = 15;
        let animTimer = null;

        function animateProgress() {
            if (displayed < target) {
                displayed = Math.min(target, displayed + 1);
                progress.set(displayed);
            }
            animTimer = setTimeout(animateProgress, 60);
        }
        animateProgress();

        async function poll() {
            try {
                const { data } = await axios.get(`/translate/${taskId}`);

                if (data.status === 'failed') {
                    return { __failed: true, data };
                }

                if (data.status && data.status !== 'completed') {
                    // Slow crawl while "in progress"
                    target = Math.min(75, displayed + 5);
                    return false;
                }

                // Completed — count finished languages to set the final 100%
                const finished = Array.isArray(data.translations) ? data.translations.length : 0;
                const ratio = expectedLanguages
                    ? Math.min(1, finished / expectedLanguages)
                    : 1;
                target = 100;
                // Let the smooth animation catch up to 100
                return data;
            } catch (err) {
                console.error(err);
                notify({
                    type: 'error',
                    title: `Task #${taskId} failed`,
                    message: err.response?.data?.detail || err.message || 'Unknown error',
                });
                throw err;
            }
        }

        let resultData;
        try {
            while (!resultData) {
                await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
                const polled = await poll();
                if (polled && polled.__failed) {
                    if (animTimer) clearTimeout(animTimer);
                    notify({
                        type: 'error',
                        title: `Task #${taskId} failed`,
                        message: 'The translation service could not complete this request. Please try again.',
                    });
                    progressContainer.classList.remove('visible');
                    btn.disabled = false;
                    btn.innerHTML = 'Translate';
                    return;
                }
                resultData = polled;
            }
        } catch {
            if (animTimer) clearTimeout(animTimer);
            progressContainer.classList.remove('visible');
            btn.disabled = false;
            btn.innerHTML = 'Translate';
            return;
        }

        // Hold at 100% briefly so the user perceives completion
        await new Promise((r) => setTimeout(r, 400));
        if (animTimer) clearTimeout(animTimer);
        progress.set(100);

        // Render results
        const translations = resultData.translations || [];
        let html = `
            <span class="section-label">Results</span>
            <h2 class="section-title">Your <span class="accent">Translations</span></h2>
            <div class="result-task">Task <strong>#${taskId}</strong> — ${translations.length} language(s)</div>
        `;
        if (translations.length === 0) {
            html += `<div class="result-empty">No translations were returned.</div>`;
        } else {
            translations.forEach((t) => {
                html += `
                    <div class="result-card">
                        <div class="result-header">
                            <span class="result-lang">${escapeHtml(t.language)}</span>
                        </div>
                        <div class="result-text">${escapeHtml(t.translated_text)}</div>
                    </div>
                `;
            });
        }
        resultsArea.innerHTML = html;
        resultsArea.classList.add('visible');

        // Auto-fill the task ID in the "Check Status" form for convenience
        const idInput = document.getElementById('translation-id');
        if (idInput) idInput.value = taskId;

        // Reset state for the next request
        setTimeout(() => {
            progressContainer.classList.remove('visible');
            btn.disabled = false;
            btn.innerHTML = 'Translate';
        }, 800);

        notify({
            type: 'success',
            title: 'Translation complete',
            message: `Task #${taskId} finished — ${translations.length} language(s) ready.`,
        });
    };

    function escapeHtml(s) {
        if (s == null) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // -----------------------------------------------------------------------
    //  Check status / content (kept from previous implementation)
    // -----------------------------------------------------------------------
    window.checkTranslationStatus = async function (e) {
        e?.preventDefault?.();
        const id = document.getElementById('translation-id').value.trim();
        if (!id) {
            notify({ type: 'error', title: 'Missing ID', message: 'Please enter a translation ID.' });
            return;
        }
        const container = document.getElementById('status-container');
        const result = document.getElementById('statusResult');
        result.textContent = 'Loading…';
        container.classList.add('visible');
        document.getElementById('content-container').classList.remove('visible');

        try {
            const { data } = await axios.get(`/translate/${id}`);
            result.textContent = JSON.stringify(
                { id: data.id, status: data.status, languages_count: data.translations?.length ?? 0 },
                null,
                2,
            );
            notify({ type: 'success', title: `Task #${id}`, message: `Status: ${data.status}` });
        } catch (err) {
            result.textContent = err.response?.data?.detail || err.message;
            notify({ type: 'error', title: 'Lookup failed', message: result.textContent });
        }
    };

    window.checkTranslationContent = async function (e) {
        e?.preventDefault?.();
        const id = document.getElementById('translation-id').value.trim();
        if (!id) {
            notify({ type: 'error', title: 'Missing ID', message: 'Please enter a translation ID.' });
            return;
        }
        const container = document.getElementById('content-container');
        const result = document.getElementById('contentResult');
        result.textContent = 'Loading…';
        container.classList.add('visible');
        document.getElementById('status-container').classList.remove('visible');

        try {
            const { data } = await axios.get(`/translate/${id}`);
            result.textContent = JSON.stringify(data, null, 2);
            notify({ type: 'success', title: `Task #${id}`, message: 'Content loaded.' });
        } catch (err) {
            result.textContent = err.response?.data?.detail || err.message;
            notify({ type: 'error', title: 'Lookup failed', message: result.textContent });
        }
    };
})();
