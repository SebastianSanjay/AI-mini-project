document.addEventListener("DOMContentLoaded", () => {
    const jobId = sessionStorage.getItem('linguafuse_job_id');

    if (!jobId) {
        window.location.href = 'upload.html';
        return;
    }

    const logFeed = document.getElementById('log-feed');
    const progressBar = document.getElementById('pipeline-progress-bar');
    const progressPercent = document.getElementById('pipeline-percent');
    const cancelBtn = document.getElementById('cancel-btn');

    let wsClient = null;
    let fallbackInterval = null;

    // Ordered list of steps mapping to DB values
    const stepOrder = [
        "upload", "extraction", "transcription",
        "translation", "voice_generation", "lip_sync", "rendering", "complete"
    ];

    function appendLog(message, type="info") {
        const div = document.createElement('div');
        div.className = `log-line log-${type}`;

        const timestamp = new Date().toISOString().split('T')[1].substring(0,8);
        div.textContent = `[${timestamp}] > ${message}`;

        logFeed.appendChild(div);
        logFeed.scrollTop = logFeed.scrollHeight;
    }

    function updateUI(data) {
        // Update Progress Bar
        const prog = parseFloat(data.progress || 0).toFixed(1);
        progressBar.style.width = `${prog}%`;
        progressPercent.textContent = `${Math.round(prog)}%`;

        // Update Step List
        const currentStep = data.current_step || data.step;
        const currentStepIndex = stepOrder.indexOf(currentStep);

        document.querySelectorAll('.step-item').forEach(item => {
            const itemStep = item.getAttribute('data-step');
            const itemIndex = stepOrder.indexOf(itemStep);

            item.classList.remove('active', 'completed', 'pending', 'error');

            if (data.status === 'failed') {
                if (itemStep === currentStep) item.classList.add('error');
                else if (itemIndex < currentStepIndex) item.classList.add('completed');
                else item.classList.add('pending');
            } else {
                if (itemIndex < currentStepIndex) {
                    item.classList.add('completed');
                } else if (itemIndex === currentStepIndex) {
                    item.classList.add('active');
                } else {
                    item.classList.add('pending');
                }
            }
        });

        // Add to log
        if (data.message) {
            appendLog(data.message, data.status === 'failed' ? 'error' : 'info');
        } else if (data.status === 'failed' && data.error) {
            appendLog(`ERROR: ${data.error}`, 'error');
        }

        // Handle Completion/Failure
        if (data.status === 'completed') {
            appendLog("Processing complete. Redirecting to results...", "success");
            setTimeout(() => {
                window.location.href = 'result.html';
            }, 2000);
        } else if (data.status === 'failed') {
            appendLog("Processing failed. Please try again.", "error");
            cancelBtn.textContent = "Return to Dashboard";
        }
    }

    // Polling fallback if WS fails
    async function pollStatus() {
        try {
            const res = await fetch(`${API_BASE}/processing-status/${jobId}`);
            if (res.ok) {
                const data = await res.json();
                updateUI(data);

                if (data.status === 'completed' || data.status === 'failed') {
                    clearInterval(fallbackInterval);
                }
            }
        } catch (e) {
            console.error("Polling error", e);
        }
    }

    // Initialize Connection
    appendLog(`Initializing connection for job ${jobId}...`);

    if (window.WebSocket) {
        wsClient = new WebSocketClient(
            jobId,
            updateUI,
            (finalData) => {
                clearInterval(fallbackInterval);
            },
            (err) => {
                appendLog("WebSocket connection issue, falling back to polling.", "error");
                if (!fallbackInterval) fallbackInterval = setInterval(pollStatus, 3000);
            }
        );
        wsClient.connect();
    } else {
        appendLog("WebSockets not supported by browser. Using polling.");
        fallbackInterval = setInterval(pollStatus, 3000);
    }

    // Cancel Button
    cancelBtn.addEventListener('click', () => {
        if (wsClient) wsClient.disconnect();
        if (fallbackInterval) clearInterval(fallbackInterval);
        sessionStorage.removeItem('linguafuse_job_id');
        window.location.href = 'upload.html';
    });

    // Initial poll to get current state immediately
    pollStatus();
});