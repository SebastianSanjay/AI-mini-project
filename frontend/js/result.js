document.addEventListener("DOMContentLoaded", async () => {
    const jobId = sessionStorage.getItem('linguafuse_job_id');

    if (!jobId) {
        window.location.href = 'upload.html';
        return;
    }

    const videoElement = document.getElementById('final-video');
    const loader = document.getElementById('video-loader');
    const downloadBtn = document.getElementById('download-btn');

    try {
        // Verify job status first
        const statusRes = await fetch(`${API_BASE}/processing-status/${jobId}`);
        if (!statusRes.ok) throw new Error("Failed to verify job status");
        const statusData = await statusRes.json();

        if (statusData.status !== 'completed') {
            alert("Video is not ready yet.");
            window.location.href = 'processing.html';
            return;
        }

        // Setup Video Player via Blob or direct src
        const videoUrl = `${API_BASE}/download/${jobId}`;

        videoElement.src = videoUrl;
        videoElement.onloadstart = () => {
            loader.classList.add('hidden');
            videoElement.classList.remove('hidden');
        };

        // Setup Download Button
        downloadBtn.addEventListener('click', () => {
            // Create a temporary link to trigger download attribute behavior
            const a = document.createElement('a');
            a.href = videoUrl;
            a.download = `translated_video_${jobId}.mp4`; // The backend sets Content-Disposition as well
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });

    } catch (error) {
        console.error("Error loading result:", error);
        alert("There was an error retrieving your video.");
        loader.classList.add('hidden');
    }
});