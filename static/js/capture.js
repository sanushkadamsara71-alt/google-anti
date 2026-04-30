document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const snapshot = document.getElementById('snapshot');
    const captureBtn = document.getElementById('captureBtn');
    const retakeBtn = document.getElementById('retakeBtn');
    const captureSubmitBtn = document.getElementById('captureSubmitBtn');
    const overlay = document.querySelector('.overlay-guideline');

    let stream;
    let currentImageB64 = null;

    // Start Webcam
    async function startWebcam() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
            video.srcObject = stream;
        } catch (err) {
            console.error("Error accessing webcam: ", err);
            alert("Could not access webcam. Please ensure permissions are granted.");
        }
    }

    startWebcam();

    captureBtn.addEventListener('click', () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        
        currentImageB64 = canvas.toDataURL('image/jpeg');
        snapshot.src = currentImageB64;
        
        video.style.display = 'none';
        overlay.style.display = 'none';
        snapshot.style.display = 'block';
        
        captureBtn.style.display = 'none';
        retakeBtn.style.display = 'block';
        captureSubmitBtn.disabled = false;
    });

    retakeBtn.addEventListener('click', () => {
        video.style.display = 'block';
        overlay.style.display = 'block';
        snapshot.style.display = 'none';
        
        captureBtn.style.display = 'block';
        retakeBtn.style.display = 'none';
        captureSubmitBtn.disabled = true;
        currentImageB64 = null;
    });

    captureSubmitBtn.addEventListener('click', async () => {
        const studentRoll = document.getElementById('studentRoll').value.trim();
        const studentName = document.getElementById('studentName').value.trim();

        if (!studentRoll || !studentName) {
            alert("Please fill in both Student ID and Name.");
            return;
        }

        captureSubmitBtn.disabled = true;
        captureSubmitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';

        try {
            const response = await fetch('/api/students/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student_roll: studentRoll,
                    name: studentName,
                    image_base64: currentImageB64
                })
            });

            const data = await response.json();
            if (data.success) {
                alert(data.message);
                window.location.href = '/students';
            } else {
                alert("Error: " + data.message);
                captureSubmitBtn.disabled = false;
                captureSubmitBtn.innerHTML = '<i class="fa-solid fa-save"></i> Save Student';
            }
        } catch (err) {
            console.error(err);
            alert("Network error.");
            captureSubmitBtn.disabled = false;
            captureSubmitBtn.innerHTML = '<i class="fa-solid fa-save"></i> Save Student';
        }
    });
});
