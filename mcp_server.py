
import os
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "KOYEL JARVIS",
    stateless_http=True,
    json_response=True
)

BACKEND_URL = os.getenv("JARVIS_BACKEND_URL", "").rstrip("/")


@mcp.tool()
def ask_jarvis(message: str) -> str:
    """
    KOYEL JARVIS AI-কে প্রশ্ন করো এবং উত্তর পাও।
    """

    if not BACKEND_URL:
        return "JARVIS Backend URL সেট করা হয়নি।"

    if not isinstance(message, str) or not message.strip():
        return "দয়া করে একটি প্রশ্ন লেখো।"

    if len(message) > 4000:
        return "প্রশ্নটি অনেক বড়। ছোট করে লেখো।"

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json={"message": message},
            timeout=50
        )

        response.raise_for_status()

        data = response.json()
        return data.get("reply", "KOYEL উত্তর দিতে পারেনি।")

    except requests.RequestException as error:
        print("JARVIS connection error:", str(error))
        return "JARVIS AI Brain-এর সঙ্গে সংযোগ করা যাচ্ছে না।"


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000"))
    )
