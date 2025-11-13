from flask import Flask, request, jsonify
import os
import openai

app = Flask(__name__)

# Load API Key securely
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable not set.")
openai.api_key = openai_api_key

@app.route("/", methods=["POST", "OPTIONS"])
def chat_handler():
    if request.method == "OPTIONS":
        return _cors_response({"status": "ok"}, 204)

    try:
        data = request.get_json()
        message = data.get("message", "")
        session_id = data.get("sessionId", "default")

        if not message:
            return _cors_response({"error": "Message required"}, 400)

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ],
            max_tokens=100
        )

        assistant_message = completion.choices[0].message.content

        return _cors_response({
            "response": assistant_message,
            "sessionId": session_id
        })

    except Exception as ex:
        return _cors_response({"error": f"Error: {str(ex)}"}, 500)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

def _cors_response(data, status=200):
    response = jsonify(data)
    response.status_code = status
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
