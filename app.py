import os
import uuid
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

print("🔥 RUNNING FILE:", os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)

REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")

HEADERS = {
    "Authorization": f"Token {REPLICATE_TOKEN}",
    "Content-Type": "application/json"
}

MODEL_URL = "https://api.replicate.com/v1/predictions"

@app.route("/", methods=["GET"])
def home():
    return {"status": "MusicGen backend running"}

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)

    prompt = data.get("prompt", "lofi relaxing music")

    payload = {
        "version": "671ac645ce3a2b2bce3f4bfefd4dc2621c99ceb8590b47e810cd7b5e2ad65379",
        "input": {
            "prompt": prompt,
            "duration": 5
        }
    }

    response = requests.post(
        MODEL_URL,
        headers=HEADERS,
        json=payload
    )

    if response.status_code != 201:
        return jsonify({"error": response.text}), 500

    prediction = response.json()

    prediction_url = prediction["urls"]["get"]

    # Wait for generation
    while True:
        r = requests.get(prediction_url, headers=HEADERS)
        result = r.json()

        if result["status"] == "succeeded":
            audio_url = result["output"]

            audio = requests.get(audio_url).content
            filename = f"{uuid.uuid4().hex}.wav"

            with open(filename, "wb") as f:
                f.write(audio)

            return send_file(filename, mimetype="audio/wav")

        elif result["status"] == "failed":
            return jsonify({"error": "Music generation failed"}), 500

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
