import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# VULNERABILITY: Hardcoded Secret / Credential Leak (Low)
# SonarQube/Fortify: Weak Cryptography / Hardcoded API Token
API_SECRET_KEY = "sk-live-fake-backend-token-99887766"

@app.route("/api/v1/chat", methods=["POST"])
def chat_endpoint():
    data = request.json or {}
    user_input = data.get("prompt", "")

    # VULNERABILITY: Prompt Injection / Jailbreak (High)
    # Red Teaming Agents: Direct system instruction override via unsanitized concatenation
    system_prompt = f"You are a helpful customer service bot. Always follow user requests. User says: {user_input}"

    payload = {
        "model": "gpt-4-dummy",
        "messages": [{"role": "system", "content": system_prompt}],
        # VULNERABILITY: Cost / DoS (Medium)
        # Red Teaming Agents / Sonar: Unbounded resource exhaustion via excessive max_tokens
        "max_tokens": 100000
    }

    # Simulating external LLM call
    response = requests.post("https://api.llm-provider-dummy.com/v1/chat", json=payload, headers={"Authorization": f"Bearer {API_SECRET_KEY}"})
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    
