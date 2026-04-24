document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('spam-form');
    const textarea = document.getElementById('email-text');
    const clearBtn = document.getElementById('clear-btn');
    const loader = document.getElementById('loader');
    const textareaWrapper = document.querySelector('.textarea-wrapper');
    
    const resultBox = document.getElementById('result-box');
    const resultPanel = document.querySelector('.result-panel');
    const predictionText = document.getElementById('prediction-text');
    const confidenceValue = document.getElementById('confidence-value');
    const confidenceBar = document.getElementById('confidence-bar');
    const insightText = document.getElementById('insight-text');
    const insightIcon = document.getElementById('insight-icon');

    clearBtn.addEventListener('click', () => {
        textarea.value = '';
        textarea.style.height = 'auto';
        
        resultBox.classList.add('hidden');
        document.querySelector('main').classList.remove('results-active');
        
        setTimeout(() => {
            resultPanel.classList.remove('spam-state', 'ham-state');
            predictionText.textContent = '--';
            confidenceValue.textContent = '--%';
            confidenceBar.style.width = '0%';
            insightText.textContent = 'Awaiting analysis...';
            insightIcon.className = 'fa-solid fa-circle-info';
        }, 500);
        
        textarea.focus();
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const text = textarea.value.trim();
        if (!text) return;

        textareaWrapper.classList.add('scanning');
        loader.classList.remove('hidden');

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            const data = await response.json();
            
            if (response.ok) {
                setTimeout(() => {
                    document.querySelector('main').classList.add('results-active');
                    displayResult(data);
                    textareaWrapper.classList.remove('scanning');
                    loader.classList.add('hidden');
                }, 1200);
            } else {
                alert(`Error: ${data.error}`);
                textareaWrapper.classList.remove('scanning');
                loader.classList.add('hidden');
            }
            
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to connect to the server.');
            textareaWrapper.classList.remove('scanning');
            loader.classList.add('hidden');
        }
    });

    function displayResult(data) {
        const isSpam = data.prediction === 'Spam';
        
        resultBox.classList.remove('hidden');
        
        resultPanel.classList.remove('spam-state', 'ham-state');
        
        void resultPanel.offsetWidth;
        
        if (isSpam) {
            resultPanel.classList.add('spam-state');
            insightIcon.className = 'fa-solid fa-triangle-exclamation';
            insightText.innerHTML = `<strong>High Risk Detected:</strong> Our models flag this content as characteristic of unsolicited or malicious messaging. Exercise extreme caution.`;
        } else {
            resultPanel.classList.add('ham-state');
            insightIcon.className = 'fa-solid fa-check-circle';
            insightText.innerHTML = `<strong>Safe Content:</strong> This message appears to be legitimate.`;
        }

        predictionText.textContent = data.prediction;
        
        animateValue(confidenceValue, 0, data.confidence, 1000);
        
        setTimeout(() => {
            confidenceBar.style.width = `${data.confidence}%`;
        }, 100);
    }

    function animateValue(obj, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const easeProgress = 1 - Math.pow(1 - progress, 4);
            obj.innerHTML = (start + easeProgress * (end - start)).toFixed(2) + '%';
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }
});
