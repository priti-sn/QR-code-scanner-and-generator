import base64
import io

import cv2
import numpy as np
import qrcode
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scanner")
def scanner():
    return render_template("scanner.html")


@app.route("/generator")
def generator():
    return render_template("generator.html")


@app.route("/scan-frame", methods=["POST"])
def scan_frame():
    """
    Receives a base64-encoded JPEG frame from the browser,
    runs OpenCV QR detection on it, and returns any decoded text.
    """
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "No image data received"}), 400

    # strip the data-url header if present
    img_data = data["image"]
    if "," in img_data:
        img_data = img_data.split(",")[1]

    # decode base64 to raw bytes, then to a numpy array for OpenCV
    try:
        raw_bytes = base64.b64decode(img_data)
        np_arr = np.frombuffer(raw_bytes, dtype=np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception:
        return jsonify({"error": "Failed to decode image"}), 400

    if frame is None:
        return jsonify({"error": "Invalid image"}), 400

    detector = cv2.QRCodeDetector()
    decoded_text, points, _ = detector.detectAndDecode(frame)

    result = {"found": False, "text": ""}
    if decoded_text:
        result["found"] = True
        result["text"] = decoded_text

    return jsonify(result)


@app.route("/generate", methods=["POST"])
def generate():
    """
    Takes text/URL from the form, creates a QR code image,
    and sends it back as a PNG download.
    """
    text = request.form.get("text", "").strip()
    if not text:
        return "No text provided", 400

    # build the QR image using the qrcode library
    qr = qrcode.QRCode(
        version=None,  # auto-size
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype="image/png", download_name="qrcode.png")


if __name__ == "__main__":
    app.run(debug=True)
