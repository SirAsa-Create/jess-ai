import os
import openai # Keep this import
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# --- NEW: Initialize the OpenRouter client ---
# This uses your environment variable to configure the client.
# The `base_url` tells the library to send requests to OpenRouter instead of OpenAI.
client = openai.OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.environ.get("OPENROUTER_API_KEY"),
)
# ----------------------------------------------

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Jess AI (OpenRouter version) is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    # It's good practice to get the user's number for future use
    user_phone_number = request.values.get("From", "") 
    print(f"[WHATSAPP RECEIVED] From: {user_phone_number}, Message: {incoming_msg}")
    
    # Ignore empty messages
    if not incoming_msg:
        return str(MessagingResponse())

    try:
        # --- UPDATED: The new API call syntax ---
        response = client.chat.completions.create(
            # Pro-tip: For free models, "mistralai/mistral-7b-instruct" is fast and powerful.
            model="openai/gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "You are Jess, a smart and helpful AI assistant. You are concise and friendly."},
                {"role": "user", "content": incoming_msg}
            ],
        )
        answer = response.choices[0].message.content.strip()
        print(f"[OPENROUTER RESPONSE] {answer}")

    except Exception as e:
        # This will now print the actual error to your Render logs, which is very helpful for debugging.
        print(f"[ERROR] OpenRouter call failed: {e}")
        answer = "Sorry, Jess had a brain freeze. Please try again in a moment."

    # Send the reply via Twilio
    reply = MessagingResponse()
    reply.message(answer)
    return str(reply)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # In production on Render, you shouldn't run in debug mode.
    # Render manages the host and port automatically.
    app.run(host="0.0.0.0", port=port)
