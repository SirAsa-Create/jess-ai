from flask import Flask, request
import openai
import os

app = Flask(__name__)

# Load your OpenAI API key securely from environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/jess", methods=["POST"])
def jess_reply():
    incoming_msg = request.values.get("Body", "").strip()

    if not incoming_msg:
        return "No message received", 400

    try:
        # Create a reply using OpenAI's ChatCompletion
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Jess, a smart and helpful WhatsApp assistant."},
                {"role": "user", "content": incoming_msg}
            ]
        )
        reply = chat.choices[0].message.content.strip()
    except Exception as e:
        reply = "Jess is confused right now. Please try again later."

    return reply, 200

@app.route("/", methods=["GET"])
def index():
    return "Jess AI is up and running!", 200

if __name__ == "__main__":
    app.run(debug=True)
