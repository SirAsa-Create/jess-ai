from flask import Flask, request
import openai
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

# Load your API key from environment
openai.api_key = os.environ['OPENAI_API_KEY']

@app.route("/", methods=["GET"])
def index():
    return "Jess AI is up and running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    print(f"[Incoming Message] {incoming_msg}")

    resp = MessagingResponse()
    msg = resp.message()

    try:
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Jess, a helpful, witty WhatsApp AI assistant."},
                {"role": "user", "content": incoming_msg}
            ]
        )
        reply = chat.choices[0].message.content.strip()
        print(f"[AI Reply] {reply}")
        msg.body(reply)

    except Exception as e:
        print(f"[Error] {e}")
        msg.body("Sorry, Jess had a little brain freeze 😵. Please try again later.")

    return str(resp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
