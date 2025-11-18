from flask import Flask, render_template, request, send_file, redirect, url_for
import qrcode
import os
import base64
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

passwords = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    password = request.form.get("password", "")
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    passwords[filename] = password

    # -------- FIXED QR CODE LINK (uses your WiFi IP) --------
    server_ip = "192.168.1.8"  # YOUR IPv4 address
    download_url = f"http://{server_ip}:5000" + url_for("verify", filename=filename)
    # --------------------------------------------------------

    # generate QR code
    img = qrcode.make(download_url)

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    qr_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return render_template("qr.html", qr_image=qr_b64, download_url=download_url, filename=filename)

@app.route("/verify/<filename>", methods=["GET", "POST"])
def verify(filename):
    if request.method == "POST":
        entered = request.form.get("password", "")
        if entered == passwords.get(filename):
            return redirect(url_for("download", filename=filename))
        return "Wrong password!", 401

    return render_template("password.html", filename=filename)

@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
