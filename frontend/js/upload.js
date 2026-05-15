document.addEventListener("DOMContentLoaded", () => {
    // Populate dropdowns from config.js
    populateLanguageDropdown("target-language");
    populateLanguageDropdown("source-language");

    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const startBtn = document.getElementById('start-btn');
    const startHelper = document.getElementById('start-helper');

    const previewContainer = document.getElementById('video-preview-container');
    const videoPreview = document.getElementById('video-preview');
    const fileInfoDisplay = document.getElementById('file-info-display');
    const removeFileBtn = document.getElementById('remove-file-btn');

    const targetLangSelect = document.getElementById('target-language');
    const sourceLangSelect = document.getElementById('source-language');

    const progressContainer = document.getElementById('upload-progress-container');
    const progressBar = document.getElementById('upload-progress-bar');
    const progressPercent = document.getElementById('upload-percent');

    let selectedFile = null;

    // --- Drag and Drop Handlers ---
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.remove('dragover');
        }, false);
    });

    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    });

    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    removeFileBtn.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = "";
        previewContainer.classList.add('hidden');
        videoPreview.src = "";
        checkReadyState();
    });

    targetLangSelect.addEventListener('change', checkReadyState);

    // --- File Handling & Validation ---
    function handleFiles(files) {
        if (files.length === 0) return;

        const file = files[0];

        // Validate type
        const validTypes = ['video/mp4', 'video/quicktime', 'video/x-matroska', 'video/avi'];
        if (!validTypes.includes(file.type) && !file.name.match(/\.(mp4|mov|mkv|avi|prores)$/i)) {
            alert('Invalid file format. Please upload MP4, MOV, or MKV.');
            return;
        }

        // Validate size (25GB limit = 25 * 1024 * 1024 * 1024 bytes)
        const maxSize = 25n * 1024n * 1024n * 1024n;
        if (BigInt(file.size) > maxSize) {
            alert('File exceeds the 25GB maximum limit.');
            return;
        }

        selectedFile = file;

        // Setup preview
        const fileURL = URL.createObjectURL(file);
        videoPreview.src = fileURL;
        fileInfoDisplay.textContent = `${file.name} (${(file.size / (1024*1024)).toFixed(2)} MB)`;
        previewContainer.classList.remove('hidden');

        checkReadyState();
    }

    function checkReadyState() {
        if (selectedFile && targetLangSelect.value) {
            startBtn.disabled = false;
            startBtn.classList.remove('disabled');
            startHelper.textContent = "Ready for processing";
        } else {
            startBtn.disabled = true;
            startBtn.classList.add('disabled');
            if (!selectedFile) startHelper.textContent = "Upload a file to proceed";
            else if (!targetLangSelect.value) startHelper.textContent = "Select a target language";
        }
    }

    // --- Upload Logic ---
    startBtn.addEventListener('click', async () => {
        if (!selectedFile || startBtn.disabled) return;

        // UI Updates
        startBtn.disabled = true;
        startBtn.innerHTML = '<span class="pulse-soft">⏳</span> Uploading...';
        progressContainer.classList.remove('hidden');
        removeFileBtn.disabled = true;

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('target_language', targetLangSelect.value);
        if (sourceLangSelect.value) {
            formData.append('source_language', sourceLangSelect.value);
        }

        try {
            // Using XMLHttpRequest for upload progress tracking
            const xhr = new XMLHttpRequest();

            xhr.upload.addEventListener("progress", (event) => {
                if (event.lengthComputable) {
                    const percentComplete = Math.round((event.loaded / event.total) * 100);
                    progressBar.style.width = percentComplete + '%';
                    progressPercent.textContent = percentComplete + '%';
                }
            });

            const uploadPromise = new Promise((resolve, reject) => {
                xhr.onload = () => {
                    if (xhr.status >= 200 && xhr.status < 300) resolve(JSON.parse(xhr.responseText));
                    else reject(new Error(xhr.responseText || "Upload failed"));
                };
                xhr.onerror = () => reject(new Error("Network error during upload"));

                xhr.open("POST", `${API_BASE}/upload-video`, true);
                // Important: Do not set Content-Type header manually when sending FormData
                xhr.send(formData);
            });

            const uploadResult = await uploadPromise;
            const jobId = uploadResult.job_id;

            if (!jobId) throw new Error("No job ID returned from server.");

            // Step 2: Trigger Translation
            document.getElementById('upload-status-text').textContent = "Initializing engines...";

            const transRes = await fetch(`${API_BASE}/translate-video/${jobId}`, { method: 'POST' });
            if (!transRes.ok) throw new Error("Failed to start translation pipeline");

            // Store ID and redirect
            sessionStorage.setItem('linguafuse_job_id', jobId);
            window.location.href = 'processing.html';

        } catch (error) {
            console.error(error);
            alert(`Error: ${error.message}`);
            startBtn.disabled = false;
            startBtn.innerHTML = '<span class="btn-icon">⚡</span> Start Translation';
            progressContainer.classList.add('hidden');
            removeFileBtn.disabled = false;
        }
    });
});