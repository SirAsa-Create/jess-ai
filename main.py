from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os

app = Flask(__name__)

# Load OpenAI API key from environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/jess", methods=["POST"])
def jess_reply():
    incoming_msg = request.values.get("Body", "").strip()

    # Prepare Twilio response
    resp = MessagingResponse()
    msg = resp.message()

    if not incoming_msg:
        msg.body("I didn't receive any message 😕")
        return str(resp)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Jess, a helpful, witty WhatsApp AI assistant."},
                {"role": "user", "content": incoming_msg}
            ]
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = "Jess is confused right now 🤯. Try again later."

    msg.body(reply)
    return str(resp)

@app.route("/", methods=["GET"])
def home():
    return "Jess AI is live and ready!", 200

if __name__ == "__main__":
    app.run(debug=True)
