from flask import Flask, request, jsonify
import os
from anthropic import Anthropic

app = Flask(__name__)

# Initialize Anthropic client using only API key
anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# In-memory conversation tracking (for demo purposes)
conversations = {}

@app.route("/", methods=["POST", "OPTIONS"])
def chat_handler(request):
    """Chat endpoint for Cloud Run."""

    # Handle CORS preflight
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response, 204

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        user_message = data.get("message", "")
        session_id = data.get("sessionId", "default")

        if not user_message:
            return jsonify({"error": "Message required"}), 400

        # Initialize session
        if session_id not in conversations:
            conversations[session_id] = []

        # Add user message
        conversations[session_id].append({
            "role": "user",
            "content": user_message
        })

        # Trim history to last 10 messages
        if len(conversations[session_id]) > 10:
            conversations[session_id] = conversations[session_id][-10:]

        # Call Anthropic API
        response = anthropic_client.messages.create(
            model="claude-2.1",
            max_tokens=128,
            messages=conversations[session_id]
        )

        assistant_message = response.content[0].text

        # Add assistant response
        conversations[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        # Return response with CORS headers
        result = jsonify({
            "response": assistant_message,
            "sessionId": session_id
        })
        result.headers["Access-Control-Allow-Origin"] = "*"
        return result, 200

    except Exception as e:
        result = jsonify({"error": f"Error: {str(e)}"})
        result.headers["Access-Control-Allow-Origin"] = "*"
        return result, 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200
