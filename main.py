import os
import json
import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# --- Database Setup ---
USER_DB = "users.json"

# --- OpenAI Client Setup ---
# Using OpenRouter, but ready for a switch to a direct paid API
client = openai.OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# --- Data Helper Functions ---
def load_users():
    """Loads the user database from the JSON file."""
    if not os.path.exists(USER_DB):
        with open(USER_DB, 'w') as f:
            json.dump({}, f)
        return {}
    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_users(users_data):
    """Saves the user database to the JSON file."""
    with open(USER_DB, "w") as f:
        json.dump(users_data, f, indent=4)

# --- Command Handlers ---

def handle_memory_command(message, user_data):
    """Handles commands like 'remember that...' or 'what is...'"""
    # Example: "remember that my wife's birthday is on 28 August"
    if message.startswith("remember that"):
        fact = message.replace("remember that", "").strip()
        # Simple key-value, we can make this smarter later
        key, value = fact.split(" is ", 1)
        user_data["memory"][key.strip()] = value.strip()
        return f"✅ Got it. I'll remember that {key.strip()} is {value.strip()}."
    
    # Example: "what is my wife's birthday"
    if message.startswith("what is"):
        key = message.replace("what is", "").replace("?", "").strip()
        answer = user_data["memory"].get(key)
        if answer:
            return f"💡 From my memory, {key} is {answer}."
        else:
            return f"🤔 I don't have a memory for '{key}'."
    return None

def handle_crm_command(message, user_data):
    """Handles simple CRM commands"""
    parts = message.split()
    command = parts[0]

    # Example: "new client Ali phone 0123456789"
    if command == "new" and parts[1] == "client":
        name = parts[2].capitalize()
        phone_index = parts.index("phone")
        phone = parts[phone_index + 1]
        user_data["crm"][name] = {"phone": phone, "notes": ""}
        return f"✅ New client '{name}' saved with phone {phone}."

    # Example: "note for Ali he owes RM200 for nasi lemak"
    if command == "note" and parts[1] == "for":
        name = parts[2].capitalize()
        if name in user_data["crm"]:
            note = " ".join(parts[3:])
            user_data["crm"][name]["notes"] = note
            return f"✅ Note added for {name}."
        else:
            return f"❌ Client '{name}' not found."

    # Example: "find Ali"
    if command == "find":
        name = parts[1].capitalize()
        client_data = user_data["crm"].get(name)
        if client_data:
            return f"Found client: {name}\nPhone: {client_data['phone']}\nNotes: {client_data['notes']}"
        else:
            return f"❌ Client '{name}' not found."
    return None


# --- Main Flask App ---
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Jess AI is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    # Load all user data and get current user
    all_users = load_users()
    wa_from_number = request.values.get("From", "")
    user_profile = all_users.setdefault(wa_from_number, {
        "profile": {}, "memory": {}, "crm": {}, "custom_replies": {}
    })
    
    incoming_msg = request.values.get("Body", "").strip()
    response_text = None
    
    # --- Intent Router ---
    # The message is passed to handlers. If a handler returns a response, we use it.
    lower_msg = incoming_msg.lower()
    
    # Order matters. Check for the most specific commands first.
    response_text = handle_memory_command(lower_msg, user_profile)
    if not response_text:
        response_text = handle_crm_command(lower_msg, user_profile)
    
    # --- If no command was triggered, call the AI ---
    if not response_text:
        system_prompt = f"""You are Jess, a helpful AI assistant.
        The user's name is {user_profile.get('profile', {}).get('name', 'not set')}.
        """
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": incoming_msg}
            ]
        )
        response_text = response.choices[0].message.content.strip()

    # Save any changes made by the handlers
    save_users(all_users)

    # Send the reply
    reply = MessagingResponse()
    reply.message(response_text)
    return str(reply)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
