document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('translator-form');
    const btn = form.querySelector('button[type="submit"]');
    const originalBtnText = btn.innerText;
    const textArea = document.getElementById('input-text');
    const langInput = document.getElementById('languages');
    const resultsArea = document.getElementById('results');

    // Create Helix loader
    const loader = document.createElement('div');
    loader.id = 'helix-loader';
    loader.className = 'helix-loader';
    // Style the loader container
    loader.style.cssText = `
        display: none;
        gap: 6px;
        justify-content: center;
        align-items: center;
        margin: 20px 0 10px;
        min-height: 60px;
    `;

    // Create 15 columns of 3 dots each
    for (let col = 0; col < 15; col++) {
        const column = document.createElement('div');
        column.style.display = 'flex';
        column.style.flexDirection = 'column';
        column.style.gap = '4px';

        for (let row = 0; row < 3; row++) {
            const dot = document.createElement('div');
            dot.className = 'helix-dot';
            // Style base dot
            dot.style.cssText = `
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background-color: #4a4a4a;
                opacity: 0.3;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            `;
            column.appendChild(dot);
        }
        loader.appendChild(column);
    }

    // Insert loader after the form groups but before the button
    const lastFormGroup = form.querySelectorAll('.form-group');
    if (lastFormGroup.length > 0) {
        lastFormGroup[lastFormGroup.length - 1].insertAdjacentElement('afterend', loader);
    } else {
        form.insertBefore(loader, btn);
    }

    // Animation control
    let animationInterval;

    function showLoading() {
        loader.style.display = 'flex';
        btn.disabled = true;
        btn.innerText = 'Translating...';
        resultsArea.classList.remove('visible');
        startAnimation();
    }

    function hideLoading() {
        loader.style.display = 'none';
        btn.disabled = false;
        btn.innerText = originalBtnText;
        stopAnimation();
    }

    function startAnimation() {
        const columns = loader.children;
        const totalCols = columns.length;
        let time = 0;
        const speed = 0.08;

        animationInterval = setInterval(() => {
            time += speed;

            for (let i = 0; i < totalCols; i++) {
                const column = columns[i];
                const dots = column.children;

                // Sine wave calculation
                const sineValue = Math.sin(time + (i * 0.4));
                const normalizedSine = (sineValue + 1) / 2; // 0 to 1

                // Determine active row based on sine wave
                const activeRow = Math.floor(normalizedSine * 3);

                for (let j = 0; j < dots.length; j++) {
                    const dot = dots[j];

                    if (j === activeRow) {
                        // Active strand - brighter
                        dot.style.backgroundColor = '#E85D22';
                        dot.style.opacity = '1';
                        dot.style.transform = 'scale(1.2)';
                        dot.style.boxShadow = '0 0 8px rgba(232, 93, 34, 0.6)';
                    } else if (Math.abs(j - activeRow) === 1) {
                        // Near strand - medium brightness
                        dot.style.backgroundColor = '#E85D22';
                        dot.style.opacity = '0.5';
                        dot.style.transform = 'scale(1)';
                        dot.style.boxShadow = 'none';
                    } else {
                        // Far strand - dim
                        dot.style.backgroundColor = '#4a4a4a';
                        dot.style.opacity = '0.2';
                        dot.style.transform = 'scale(0.8)';
                        dot.style.boxShadow = 'none';
                    }
                }
            }
        }, 50);
    }

    function stopAnimation() {
        if (animationInterval) {
            clearInterval(animationInterval);
            animationInterval = null;
        }
        // Reset dots to base state
        const dots = loader.querySelectorAll('.helix-dot');
        dots.forEach(dot => {
            dot.style.backgroundColor = '#4a4a4a';
            dot.style.opacity = '0.3';
            dot.style.transform = 'scale(1)';
            dot.style.boxShadow = 'none';
        });
    }

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const text = textArea.value.trim();
        const languages = langInput.value.trim();

        if (!text) {
            alert('Please enter some text to translate.');
            return;
        }

        showLoading();

        // Build the payload
        const payload = {
            text: text,
            languages: languages ? languages.split(',').map(l => l.trim()).filter(Boolean) : []
        };

        console.log('Sending translation request:', payload);

        // Mock API call (replace with actual fetch in production)
        setTimeout(() => {
            hideLoading();

            // Construct mock results
            const mockResults = [
                { lang: 'FR — French', text: 'Ceci est une traduction g\u00e9n\u00e9r\u00e9e par d\u00e9faut pour la d\u00e9monstration.' },
                { lang: 'ES — Spanish', text: 'Esta es una traducci\u00f3n generada por defecto para la demostraci\u00f3n.' },
                { lang: 'JP — Japanese', text: '\u3053\u308c\u306f\u30c7\u30e2\u30f3\u30b9\u30c8\u30ec\u30fc\u30b7\u30e7\u30f3\u7528\u306e\u30c7\u30d5\u30a9\u30eb\u30c8\u3067\u751f\u6210\u3055\u308c\u305f\u7ffb\u8a33\u3067\u3059\u3002' }
            ];

            // Build results HTML
            let resultsHTML = `
                <span class="section-label">Results</span>
                <h2 class="section-title">Your <span class="accent">Translations</span></h2>
            `;

            mockResults.forEach(res => {
                resultsHTML += `
                    <div class="result-card">
                        <div class="result-header">
                            <span class="result-lang">${res.lang}</span>
                        </div>
                        <div class="result-text">${res.text}</div>
                    </div>
                `;
            });

            resultsArea.innerHTML = resultsHTML;
            resultsArea.classList.add('visible');

            // Scroll to results
            resultsArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 2000); // Simulate 2 second delay
    });
});
