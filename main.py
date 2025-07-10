import os
import json # NEW: Import the json library to work with the user file
import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# The path for our user database file
USER_DB = "users.json"

client = openai.OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# --- NEW: Helper functions to manage user data ---
def load_users():
    """Loads the user database from the JSON file."""
    if not os.path.exists(USER_DB):
        return {}
    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Handle case where file is empty or corrupt
        return {}

def save_users(users_data):
    """Saves the user database to the JSON file."""
    with open(USER_DB, "w") as f:
        json.dump(users_data, f, indent=4)
# ----------------------------------------------------

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Jess AI (Multi-User version) is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    # Load all user data from our file
    users = load_users()
    
    incoming_msg = request.values.get("Body", "").strip()
    user_phone_number = request.values.get("From", "") 
    print(f"[WHATSAPP RECEIVED] From: {user_phone_number}, Message: {incoming_msg}")

    # NEW: Get the user's profile, or create one if they are new
    user_profile = users.get(user_phone_number, {})
    user_name = user_profile.get("name") # Will be None if not set

    # NEW: A simple command to set the user's name
    if incoming_msg.lower().startswith("my name is"):
        # Extracts the name from the message
        name = incoming_msg[11:].strip()
        user_profile["name"] = name
        users[user_phone_number] = user_profile
        save_users(users)
        answer = f"Got it! I'll remember you as {name}."
        
        reply = MessagingResponse()
        reply.message(answer)
        return str(reply)
    
    # NEW: Personalize the system prompt if we know the user's name
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
                {"role": "system", "content": system_prompt}, # Use the personalized prompt
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
