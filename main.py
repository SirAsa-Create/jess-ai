import os
import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Initialize the OpenRouter client using your environment variable
client = openai.OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.environ.get("OPENROUTER_API_KEY"),
)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Jess AI (OpenRouter version) is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    user_phone_number = request.values.get("From", "") 
    print(f"[WHATSAPP RECEIVED] From: {user_phone_number}, Message: {incoming_msg}")
    
    if not incoming_msg:
        return str(MessagingResponse())

    try:
        # Attempt to get a response from the AI model
        response = client.chat.completions.create(
            # --- THIS LINE IS NOW FIXED ---
            model="mistralai/mistral-7b-instruct:free", 
            messages=[
                {"role": "system", "content": "You are Jess, a smart and helpful AI assistant. You are concise and friendly."},
                {"role": "user", "content": incoming_msg}
            ],
        )
        answer = response.choices[0].message.content.strip()
        print(f"[OPENROUTER RESPONSE] {answer}")

    except Exception as e:
        # This line prints the specific error to your Render logs
        print(f"[ERROR] OpenRouter call failed: {e}") 
        answer = "Sorry, Jess had a brain freeze. Please try again in a moment."

    # Send the reply via Twilio
    reply = MessagingResponse()
    reply.message(answer)
    return str(reply)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
