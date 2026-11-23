
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024

# Frontend origin পরে নির্দিষ্ট করা যাবে
frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")
CORS(app, resources={
    r"/api/*": {"origins": frontend_origin}
})

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """
তুমি JARVIS, তোমার AI Character-এর নাম KOYEL।
তুমি একজন বুদ্ধিমান ও বন্ধুসুলভ AI Assistant।
সবসময় সহজ, পরিষ্কার বাংলায় উত্তর দেবে।
ব্যবহারকারী অন্য ভাষায় চাইলে সেই ভাষায় উত্তর দেবে।
নিজেকে KOYEL হিসেবে পরিচয় দেবে।
"""

@app.route("/")
def home():
    return "JARVIS AI Brain is running!"

@app.route("/api/health")
def health():
    return jsonify({
        "status": "online",
        "assistant": "KOYEL"
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        if not GEMINI_API_KEY:
            return jsonify({
                "reply": "AI API Key সেট করা হয়নি।"
            }), 503

        data = request.get_json(silent=True) or {}

        message = data.get("message", "")

        if not isinstance(message, str):
            return jsonify({"reply": "সঠিক মেসেজ পাঠাও।"}), 400

        message = message.strip()

        if not message:
            return jsonify({"reply": "তোমার মেসেজটি খালি।"}), 400

        if len(message) > 4000:
            return jsonify({
                "reply": "মেসেজটি অনেক বড়। ছোট করে পাঠাও।"
            }), 400

        history = data.get("history", [])

        if not isinstance(history, list):
            history = []

        contents = []

        for item in history[-10:]:
            if not isinstance(item, dict):
                continue

            role = item.get("role")
            content = item.get("content")

            if role not in ("user", "assistant"):
                continue

            if not isinstance(content, str) or not content.strip():
                continue

            contents.append({
                "role": "user" if role == "user" else "model",
                "parts": [{"text": content[:4000]}]
            })

        contents.append({
            "role": "user",
            "parts": [{"text": message}]
        })

        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{MODEL}:generateContent"
        )

        response = requests.post(
            url,
            params={"key": GEMINI_API_KEY},
            json={
                "systemInstruction": {
                    "parts": [{"text": SYSTEM_PROMPT}]
                },
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 700
                }
            },
            timeout=45
        )

        if not response.ok:
            print("Gemini API error:", response.status_code)
            return jsonify({
                "reply": "AI Brain এখন ব্যস্ত। একটু পরে চেষ্টা করো।"
            }), 502

        result = response.json()

        candidates = result.get("candidates", [])

        if not candidates:
            return jsonify({
                "reply": "এখন উত্তর তৈরি করা যাচ্ছে না।"
            }), 502

        parts = candidates[0].get("content", {}).get("parts", [])

        reply = " ".join(
            part["text"]
            for part in parts
            if isinstance(part.get("text"), str)
        ).strip()

        if not reply:
            reply = "আমি এখন উত্তর দিতে পারছি না।"

        return jsonify({"reply": reply})

    except requests.Timeout:
        return jsonify({
            "reply": "উত্তর পেতে বেশি সময় লাগছে। আবার চেষ্টা করো।"
        }), 504

    except Exception as error:
        print("KOYEL Error:", str(error))

        return jsonify({
            "reply": "দুঃখিত, KOYEL-এর AI Brain-এ সমস্যা হচ্ছে।"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
