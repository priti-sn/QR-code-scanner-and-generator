var video = document.getElementById("webcam");
var canvas = document.getElementById("capture-canvas");
var ctx = canvas.getContext("2d");
var resultText = document.getElementById("result-text");
var startBtn = document.getElementById("start-btn");
var stopBtn = document.getElementById("stop-btn");

var scanInterval = null;
var stream = null;

function startScanning() {
    // ask for camera permission
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
        .then(function (mediaStream) {
            stream = mediaStream;
            video.srcObject = stream;

            startBtn.disabled = true;
            stopBtn.disabled = false;
            resultText.textContent = "Scanning...";

            // start sending frames every 500ms
            scanInterval = setInterval(captureAndSend, 500);
        })
        .catch(function (err) {
            alert("Could not access camera: " + err.message);
        });
}

function stopScanning() {
    clearInterval(scanInterval);
    scanInterval = null;

    if (stream) {
        stream.getTracks().forEach(function (track) {
            track.stop();
        });
        stream = null;
    }

    video.srcObject = null;
    startBtn.disabled = false;
    stopBtn.disabled = true;
}

function captureAndSend() {
    if (!video.videoWidth) return;  // video not ready yet

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);

    var dataUrl = canvas.toDataURL("image/jpeg", 0.8);

    fetch("/scan-frame", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: dataUrl })
    })
    .then(function (response) { return response.json(); })
    .then(function (data) {
        if (data.found) {
            resultText.textContent = data.text;

            // if the result looks like a URL, make it a clickable link
            if (data.text.startsWith("http://") || data.text.startsWith("https://")) {
                resultText.innerHTML = '<a href="' + data.text + '" target="_blank">' + data.text + '</a>';
            }
        }
    })
    .catch(function (err) {
        console.error("scan error:", err);
    });
}
