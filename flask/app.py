# app.py (Flask Code)
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Rasa server URL
RASA_URL = "http://0.0.0.0:5005/webhooks/rest/webhook"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    print(request.data) 
    user_message = request.json.get('message')
    print(user_message)
    if not user_message:
        return jsonify({'error': 'No message provided!'}), 400

    try:
        # Sending user message to Rasa
        print(RASA_URL)
        response = requests.post(RASA_URL, json={"sender": "user", "message": user_message})
        response.raise_for_status()

        rasa_response = response.json()
        # Extract the first response text if available
        messages = [msg.get("text") for msg in rasa_response if "text" in msg]
        return jsonify(messages)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return jsonify({'error': 'Failed to connect to Rasa server: HTTP error.'}), 500
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return jsonify({'error': 'Failed to connect to Rasa server: Connection error.'}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(port=5001)
