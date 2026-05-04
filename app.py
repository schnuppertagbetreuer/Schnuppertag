from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
import os

app = Flask(__name__)
CORS(app, origins="*")

USERS = {
    # Schnuppis
    "schnuppi1":  {"password": "Abraxas2026!", "display": "Schnuppi 1",  "role": "schnuppi"},
    "schnuppi2":  {"password": "Abraxas2026!", "display": "Schnuppi 2",  "role": "schnuppi"},
    "schnuppi3":  {"password": "Abraxas2026!", "display": "Schnuppi 3",  "role": "schnuppi"},
    "schnuppi4":  {"password": "Abraxas2026!", "display": "Schnuppi 4",  "role": "schnuppi"},
    "schnuppi5":  {"password": "Abraxas2026!", "display": "Schnuppi 5",  "role": "schnuppi"},
    "schnuppi6":  {"password": "Abraxas2026!", "display": "Schnuppi 6",  "role": "schnuppi"},
    "schnuppi7":  {"password": "Abraxas2026!", "display": "Schnuppi 7",  "role": "schnuppi"},
    "schnuppi8":  {"password": "Abraxas2026!", "display": "Schnuppi 8",  "role": "schnuppi"},
    "schnuppi9":  {"password": "Abraxas2026!", "display": "Schnuppi 9",  "role": "schnuppi"},
    "schnuppi10": {"password": "Abraxas2026!", "display": "Schnuppi 10", "role": "schnuppi"},
    # Betreuer
    "betreuer1":  {"password": "Abraxas2026!", "display": "Betreuer 1",  "role": "betreuer"},
    "betreuer2":  {"password": "Abraxas2026!", "display": "Betreuer 2",  "role": "betreuer"},
    "betreuer3":  {"password": "Abraxas2026!", "display": "Betreuer 3",  "role": "betreuer"},
}

BOT_IDS = {
    "id-schnuppi1-abc":  "schnuppi1",
    "id-schnuppi2-def":  "schnuppi2",
    "id-schnuppi3-ghi":  "schnuppi3",
    "id-schnuppi4-jkl":  "schnuppi4",
    "id-schnuppi5-mno":  "schnuppi5",
    "id-schnuppi6-pqr":  "schnuppi6",
    "id-schnuppi7-stu":  "schnuppi7",
    "id-schnuppi8-vwx":  "schnuppi8",
    "id-schnuppi9-yz1":  "schnuppi9",
    "id-schnuppi10-234": "schnuppi10",
}

messages = []
message_counter = 0
custom_names = {}

def chat_key(a, b):
    return "-".join(sorted([a, b]))

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = USERS.get(data.get("username"))
    if user and user["password"] == data.get("password"):
        custom_name = data.get("custom_name", "").strip()
        if custom_name:
            custom_names[data["username"]] = custom_name
        bot_id = next((t for t, u in BOT_IDS.items() if u == data["username"]), None)
        display = custom_names.get(data["username"], user["display"])
        return jsonify({
            "success": True,
            "display_name": display,
            "username": data["username"],
            "bot_id": bot_id,
            "role": user["role"]
        })
    return jsonify({"success": False}), 401

@app.route("/api/reset", methods=["POST"])
def reset():
    global messages, message_counter, custom_names
    data = request.json
    username = data.get("username")
    user = USERS.get(username)
    if not user or user["role"] != "betreuer":
        return jsonify({"error": "Keine Berechtigung"}), 403
    messages = []
    message_counter = 0
    custom_names = {}
    return jsonify({"success": True})

@app.route("/api/chat", methods=["POST"])
def chat_send():
    global message_counter
    data = request.json
    username = data.get("username")
    to = data.get("to")
    if username not in USERS or to not in USERS:
        return jsonify({"error": "Ungültiger User"}), 400
    message_counter += 1
    display = custom_names.get(username, USERS[username]["display"])
    msg = {
        "id": message_counter,
        "chat_key": chat_key(username, to),
        "from": username,
        "to": to,
        "message": data.get("message", ""),
        "timestamp": int(time.time() * 1000),
        "display_name": display,
    }
    messages.append(msg)
    if len(messages) > 500:
        messages.pop(0)
    return jsonify({"success": True, "id": message_counter})

@app.route("/api/history/<other>", methods=["GET"])
def get_history(other):
    username = request.args.get("me")
    if not username or username not in USERS or other not in USERS:
        return jsonify([])
    key = chat_key(username, other)
    chat = [m for m in messages if m.get("chat_key") == key]
    return jsonify(chat[-50:])

@app.route("/api/poll/<other>", methods=["GET"])
def poll(other):
    username = request.args.get("me")
    since = int(request.args.get("since", 0))
    if not username or username not in USERS or other not in USERS:
        return jsonify([])
    key = chat_key(username, other)
    new = [m for m in messages if m.get("chat_key") == key and m["id"] > since]
    return jsonify(new)

@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify([{
        "username": k,
        "display": custom_names.get(k, v["display"]),
        "role": v["role"]
    } for k, v in USERS.items()])

@app.route("/api/bot/messages", methods=["GET"])
def bot_messages():
    bot_id = request.headers.get("Authorization")
    username = BOT_IDS.get(bot_id)
    if not username:
        return jsonify({"error": "Ungültige ID"}), 401
    since = int(request.args.get("since", 0))
    pending = [m for m in messages if m["id"] > since and m.get("to") == username]
    return jsonify(pending)

@app.route("/api/bot/send", methods=["POST"])
def bot_send():
    global message_counter
    bot_id = request.headers.get("Authorization")
    username = BOT_IDS.get(bot_id)
    if not username:
        return jsonify({"error": "Ungültige ID"}), 401
    data = request.json
    to = data.get("to")
    if not to or to not in USERS:
        return jsonify({"error": "Ungültiger Empfänger"}), 400
    message_counter += 1
    display = custom_names.get(username, USERS[username]["display"])
    msg = {
        "id": message_counter,
        "chat_key": chat_key(username, to),
        "from": username,
        "to": to,
        "message": data.get("message", ""),
        "timestamp": int(time.time() * 1000),
        "display_name": display,
    }
    messages.append(msg)
    if len(messages) > 500:
        messages.pop(0)
    return jsonify({"success": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
