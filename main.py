from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os

app = Flask(__name__)

# OpenAI client setup with secure API key from Replit Secrets
openai.api_key = os.environ['OPENAI_API_KEY']

@app.route("/")
def home():
    return "Jess is running ✅😍"

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    print(f"From: {sender} | Message: {incoming_msg}")

    try:
        chat = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Jess, a smart and friendly WhatsApp assistant who helps users with reminders, tasks, questions, and anything work or personal related."},
                {"role": "user", "content": incoming_msg}
            ]
        )
        reply = chat.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI Error:", e)
        reply = "Sorry, I had a brain glitch 🤖"

    response = MessagingResponse()
    response.message(reply)
    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
