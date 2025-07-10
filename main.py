import os
import json
import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

USER_DB = "users.json"

client = openai.OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.environ.get("OPENROUTER_API_KEY"),
)

def load_users():
    if not os.path.exists(USER_DB):
        return {}
    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_users(users_data):
    with open(USER_DB, "w") as f:
        json.dump(users_data, f, indent=4)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Jess AI (Smarter Multi-User version) is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    users = load_users()
    
    incoming_msg = request.values.get("Body", "").strip()
    user_phone_number = request.values.get("From", "")
    print(f"[WHATSAPP RECEIVED] From: {user_phone_number}, Message: {incoming_msg}")

    user_profile = users.get(user_phone_number, {})
    user_name = user_profile.get("name")

    # --- UPDATED: Make the command detection more flexible ---
    # We now check if the phrase is anywhere in the message.
    if "my name is" in incoming_msg.lower():
        # We split the message by the phrase to get the name
        try:
            name = incoming_msg.lower().split("my name is")[1].strip()
            # Capitalize the name for a nice touch
            name = name.capitalize() 
            
            user_profile["name"] = name
            users[user_phone_number] = user_profile
            save_users(users)
            answer = f"Got it! I'll remember that you are {name}."
        except IndexError:
            answer = "It looks like you were trying to tell me your name, but I couldn't quite catch it. Please try again, like: 'my name is [your name]'."

        reply = MessagingResponse()
        reply.message(answer)
        return str(reply)
    # -----------------------------------------------------------
    
    if user_name:
        system_prompt = f"You are Jess, a helpful AI assistant. You are currently talking to {user_name}."
    else:
        system_prompt = "You are Jess, a helpful AI assistant."

    if not incoming_msg:
        return str(MessagingResponse())

    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": incoming_msg}
            ],
        )
        answer = response.choices[0].message.content.strip()
        print(f"[OPENROUTER RESPONSE] {answer}")

    except Exception as e:
        print(f"[ERROR] OpenRouter call failed: {e}") 
        answer = "Sorry, Jess had a brain freeze. Please try again in a moment."

    reply = MessagingResponse()
    reply.message(answer)
    return str(reply)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
