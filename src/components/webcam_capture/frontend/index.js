let stream = null;
let captureInterval = null;
let countdownInterval = null;
let currentCountdown = 0;
let isActive = false;
let intervalSeconds = 5;

const video = document.getElementById('video');
const flash = document.getElementById('flash');
const indicator = document.getElementById('indicator');
const statusText = document.getElementById('status-text');
const countdownEl = document.getElementById('countdown');
const loading = document.getElementById('loading');
const error = document.getElementById('error');

function onRender(event) {
    const data = event.detail;

    if (data.active !== isActive || data.interval_seconds !== intervalSeconds) {
        isActive = data.active;
        intervalSeconds = data.interval_seconds || 5;

        if (isActive) {
            startCapture();
        } else {
            stopCapture();
        }
    }

    Streamlit.setFrameHeight(document.body.scrollHeight);
}

async function initWebcam() {
    try {
        loading.style.display = 'block';
        error.style.display = 'none';

        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'environment'
            },
            audio: false
        });

        video.srcObject = stream;
        video.style.display = 'block';
        loading.style.display = 'none';

        statusText.textContent = 'พร้อมถ่าย';

        return true;
    } catch (err) {
        console.error('Webcam error:', err);
        loading.style.display = 'none';
        error.style.display = 'block';
        error.textContent = `ไม่สามารถเข้าถึงกล้อง: ${err.message}`;

        Streamlit.setComponentValue({
            type: 'error',
            message: err.message
        });

        return false;
    }
}

function captureFrame() {
    if (!stream) return;

    try {
        flash.classList.add('active');
        setTimeout(() => flash.classList.remove('active'), 300);

        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);

        const imageData = canvas.toDataURL('image/jpeg', 0.85);

        Streamlit.setComponentValue({
            type: 'capture',
            data: imageData,
            timestamp: Date.now()
        });

        console.log('Frame captured and sent to Python');
    } catch (err) {
        console.error('Capture error:', err);
        Streamlit.setComponentValue({
            type: 'error',
            message: err.message
        });
    }
}

function updateCountdown() {
    if (currentCountdown > 0) {
        countdownEl.textContent = `ถัดไปใน: ${currentCountdown}วิ`;
        currentCountdown--;
    } else {
        countdownEl.textContent = 'กำลังถ่าย...';
    }
}

function startCapture() {
    if (!stream) {
        initWebcam().then(success => {
            if (success) startCaptureLoop();
        });
    } else {
        startCaptureLoop();
    }
}

function startCaptureLoop() {
    if (captureInterval) {
        clearInterval(captureInterval);
    }
    if (countdownInterval) {
        clearInterval(countdownInterval);
    }

    indicator.classList.remove('inactive');
    statusText.textContent = 'กำลังถ่ายอัตโนมัติ';

    captureFrame();

    currentCountdown = intervalSeconds;
    updateCountdown();

    captureInterval = setInterval(() => {
        captureFrame();
        currentCountdown = intervalSeconds;
    }, intervalSeconds * 1000);

    countdownInterval = setInterval(() => {
        updateCountdown();
    }, 1000);
}

function stopCapture() {
    if (captureInterval) {
        clearInterval(captureInterval);
        captureInterval = null;
    }
    if (countdownInterval) {
        clearInterval(countdownInterval);
        countdownInterval = null;
    }

    indicator.classList.add('inactive');
    statusText.textContent = 'หยุดชั่วคราว';
    countdownEl.textContent = '';
}

if (window.Streamlit) {
    Streamlit.setComponentReady();
    Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);

    initWebcam();
} else {
    console.error('Streamlit not found');
}

window.addEventListener('beforeunload', () => {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
});
