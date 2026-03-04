import os
import uuid
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

print("🔥 RUNNING FILE:", os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)

HF_TOKEN = os.getenv("HF_TOKEN")

HF_URL = "https://router.huggingface.co/hf-inference/models/facebook/musicgen-small?provider=hf-inference"

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "audio/wav"
}

@app.route("/", methods=["GET"])
def home():
    return {"status": "MusicGen backend running"}

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)

    prompt = data.get("prompt", "chill music")
    duration = int(data.get("duration", 5))

    response = requests.post(
        HF_URL,
        headers=HEADERS,
        json={
            "inputs": prompt,
            "parameters": {"duration": duration}
        },
        timeout=120
    )

    if response.status_code != 200:
        return jsonify({"error": response.text}), 500

    filename = f"{uuid.uuid4().hex}.wav"

    with open(filename, "wb") as f:
        f.write(response.content)

    return send_file(filename, mimetype="audio/wav")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
