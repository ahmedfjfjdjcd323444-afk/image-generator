import json
import os
import requests
from flask import Flask, request, jsonify, send_file
import uuid
import io

app = Flask(__name__)
KEYS_FILE = os.path.join(os.path.dirname(__file__), "api_keys.json")

def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_keys(keys):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=4)

def generate_key():
    return str(uuid.uuid4())

@app.route("/generate-key", methods=["POST"])
def generate_api_key():
    keys = load_keys()
    new_key = generate_key()
    keys[new_key] = True
    save_keys(keys)
    return jsonify({"api_key": new_key})

@app.route("/generate-image", methods=["POST"])
def generate_image():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400

    api_key = data.get("api_key")
    prompt = data.get("prompt")

    if not api_key or not prompt:
        return jsonify({"error": "api_key and prompt required"}), 400

    keys = load_keys()
    if api_key not in keys:
        return jsonify({"error": "invalid api key"}), 403

    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            return jsonify({"error": "image generation failed"}), 500
        img_data = resp.content
        return send_file(io.BytesIO(img_data), mimetype="image/png")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/keys", methods=["GET"])
def list_keys():
    keys = load_keys()
    return jsonify({"keys": list(keys.keys())})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
