from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
import os

app = Flask(__name__)
CORS(app, origins="*")

USERS = {
    "schueler1":  {"password": "pass123", "display": "Marco"},
    "schueler2":  {"password": "pass123", "display": "Lena"},
    "schueler3":  {"password": "pass123", "display": "David"},
    "schueler4":  {"password": "pass123", "display": "Sarah"},
    "schueler5":  {"password": "pass123", "display": "Tim"},
    "schueler6":  {"password": "pass123", "display": "Nina"},
    "schueler7":  {"password": "pass123", "display": "Finn"},
    "schueler8":  {"password": "pass123", "display": "Jana"},
    "schueler9":  {"password": "pass123", "display": "Leo"},
    "schueler10": {"password": "pass123", "display": "Mia"},
}

BOT_TOKENS = {
    "token-schueler1-abc":  "schueler1",
    "token-schueler2-def":  "schueler2",
    "token-schueler3-ghi":  "schueler3",
    "token-schueler4-jkl":  "schueler4",
    "token-schueler5-mno":  "schueler5",
    "token-schueler6-pqr":  "schueler6",
    "token-schueler7-stu":  "schueler7",
    "token-schueler8-vwx":  "schueler8",
    "token-schueler9-yz1":  "schueler9",
    "token-schueler10-234": "schueler10",
}

messages = []
last_bot_response = {}
message_counter = 0

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = USERS.get(data.get("username"))
    if user and user["password"] == data.get("password"):
        token = next((t for t, u in BOT_TOKENS.items() if u == data["username"]), None)
        return jsonify({"success": True, "display_name": user["display"], "username": data["username"], "bot_token": token})
    return jsonify({"success": False}), 401

@app.route("/api/messages", methods=["GET"])
def get_messages():
    token = request.headers.get("Authorization")
    username = BOT_TOKENS.get(token)
    if not username:
        return jsonify({"error": "Ungültiger Token"}), 401
    since = int(request.args.get("since", 0))
    pending = [m for m in messages if m["id"] > since and m.get("to") == username and m.get("type") == "user"]
    return jsonify(pending)

@app.route("/api/send", methods=["POST"])
def bot_send():
    global message_counter
    token = request.headers.get("Authorization")
    username = BOT_TOKENS.get(token)
    if not username:
        return jsonify({"error": "Ungültiger Token"}), 401
    now = time.time()
    if username in last_bot_response and now - last_bot_response[username] < 15:
        return jsonify({"error": "Rate limit"}), 429
    last_bot_response[username] = now
    data = request.json
    message_counter += 1
    msg = {
        "id": message_counter,
        "type": "bot",
        "from": username,
        "bot_name": data.get("bot_name", username + "Bot"),
        "message": data.get("message", ""),
        "timestamp": int(time.time() * 1000),
        "display_name": USERS[username]["display"]
    }
    messages.append(msg)
    if len(messages) > 200:
        messages.pop(0)
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
    msg = {
        "id": message_counter,
        "type": "user",
        "from": username,
        "to": to,
        "message": data.get("message", ""),
        "timestamp": int(time.time() * 1000),
        "display_name": USERS[username]["display"],
        "to_display": USERS[to]["display"]
    }
    messages.append(msg)
    if len(messages) > 200:
        messages.pop(0)
    return jsonify({"success": True})

@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify(messages[-50:])

@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify([{"username": k, "display": v["display"]} for k, v in USERS.items()])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
