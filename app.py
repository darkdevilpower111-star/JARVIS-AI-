k
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

SYSTEM_PROMPT = """
তুমি JARVIS।
তোমার পুরো নাম Just A Rather Very Intelligent System।
তুমি একজন বুদ্ধিমান AI Assistant।
সবসময় বাংলায় উত্তর দেবে।
সহজ, পরিষ্কার ও বন্ধুসুলভভাবে কথা বলবে।
"""

@app.route("/")
def home():
    return "JARVIS AI Brain is running!"

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}

        message = data.get("message", "").strip()
        history = data.get("history", [])

        if not message:
            return jsonify({"error": "Message is empty"}), 400

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

        for item in history[-10:]:
            if item.get("role") in ["user", "assistant"]:
                messages.append({
                    "role": item["role"],
                    "content": str(item.get("content", ""))
                })

        messages.append({
            "role": "user",
            "content": message
        })

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500
        )

        reply = response.choices[0].message.content

        return jsonify({"reply": reply})

    except Exception as e:
        print("JARVIS Error:", str(e))
        return jsonify({
            "reply": "দুঃখিত, আমার AI Brain-এ সমস্যা হচ্ছে।"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
