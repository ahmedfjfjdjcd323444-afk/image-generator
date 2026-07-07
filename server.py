from flask import Flask, request, jsonify, send_file
import requests
import io
import os

app = Flask(__name__)

VALID_KEYS = {}  # will accept any key

@app.route("/")
def home():
    return jsonify({"status": "working"})

@app.route("/generate-image", methods=["POST"])
def generate_image():
    data = request.get_json()
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "prompt required"}), 400

    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            return jsonify({"error": "image generation failed"}), 500
        return send_file(io.BytesIO(resp.content), mimetype="image/png")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
