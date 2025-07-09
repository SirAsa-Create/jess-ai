import os
import openai  # ← use legacy import
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# ✅ Set API key directly (legacy method)
openai.api_key = os.environ["OPENAI_API_KEY"]

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Jess AI is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    print(f"[WHATSAPP RECEIVED] {incoming_msg}")
    
    try:
        response = openai.ChatCompletion.create(  # legacy style
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Jess, a helpful assistant."},
                {"role": "user", "content": incoming_msg}
            ]
        )
        answer = response.choices[0].message.content.strip()
        print(f"[OPENAI RESPONSE] {answer}")

        reply = MessagingResponse()
        reply.message(answer)
        return str(reply)

    except Exception as e:
        print(f"[ERROR] {e}")
        reply = MessagingResponse()
        reply.message("Sorry, Jess had a little brain freeze. Please try again.")
        return str(reply)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
