import os
import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Jess AI (OpenRouter version) is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    print(f"[WHATSAPP RECEIVED] {incoming_msg}")
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Jess, a helpful assistant."},
                {"role": "user", "content": incoming_msg}
            ],
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api/v1"
        )
        answer = response.choices[0].message.content.strip()
        print(f"[OPENROUTER RESPONSE] {answer}")

        reply = MessagingResponse()
        reply.message(answer)
        return str(reply)

    except Exception as e:
        print(f"[ERROR] {e}")
        reply = MessagingResponse()
        reply.message("Sorry, Jess had a brain freeze (OpenRouter). Try again.")
        return str(reply)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
