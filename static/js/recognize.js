document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const toggleScannerBtn = document.getElementById('toggleScanner');
    const resultBox = document.getElementById('attendanceResult');
    const scannerStatus = document.getElementById('scannerStatus');

    let stream;
    let scanning = true;
    let scanInterval;

    async function startWebcam() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
            video.srcObject = stream;
            startScanning();
        } catch (err) {
            console.error("Error accessing webcam: ", err);
            scannerStatus.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Camera Access Denied';
            scannerStatus.style.color = 'var(--danger)';
        }
    }

    startWebcam();

    function startScanning() {
        if (!scanning) return;
        scanInterval = setInterval(processFrame, 3000); // Check every 3 seconds
    }

    function stopScanning() {
        clearInterval(scanInterval);
    }

    toggleScannerBtn.addEventListener('click', () => {
        scanning = !scanning;
        if (scanning) {
            toggleScannerBtn.innerHTML = '<i class="fa-solid fa-pause"></i> Pause Scanner';
            toggleScannerBtn.classList.remove('btn-success');
            toggleScannerBtn.classList.add('btn-warning');
            scannerStatus.innerHTML = '<div class="pulse"></div> Scanning for Faces...';
            startScanning();
        } else {
            toggleScannerBtn.innerHTML = '<i class="fa-solid fa-play"></i> Resume Scanner';
            toggleScannerBtn.classList.remove('btn-warning');
            toggleScannerBtn.classList.add('btn-success');
            scannerStatus.innerHTML = '<i class="fa-solid fa-pause"></i> Scanner Paused';
            stopScanning();
        }
    });

    async function processFrame() {
        if (!scanning) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        
        const imageB64 = canvas.toDataURL('image/jpeg');

        try {
            const response = await fetch('/api/attendance/recognize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image_base64: imageB64 })
            });

            const data = await response.json();
            
            if (data.success) {
                showResult(data.message, 'success');
                // Pause briefly on success
                stopScanning();
                setTimeout(() => { if(scanning) startScanning(); }, 4000);
            } else if (data.message !== "No face found" && data.message !== "Face not recognized") {
                // E.g. "Attendance already marked"
                showResult(data.message, 'warning');
            }
        } catch (err) {
            console.error("Analysis Error: ", err);
        }
    }

    function showResult(message, type) {
        resultBox.style.display = 'block';
        resultBox.textContent = message;
        
        if (type === 'success') {
            resultBox.className = 'result-box mt-2 result-success';
        } else {
            resultBox.className = 'result-box mt-2 result-warning';
            resultBox.style.background = 'rgba(245, 158, 11, 0.2)';
            resultBox.style.color = 'var(--warning)';
            resultBox.style.border = '1px solid var(--warning)';
        }

        setTimeout(() => {
            resultBox.style.display = 'none';
        }, 3500);
    }
});
