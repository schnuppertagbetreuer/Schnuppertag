from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
import uuid
import os

app = Flask(__name__, static_folder="../frontend")
app.config["SECRET_KEY"] = "schnuppertag2025"
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")

# ─── Vordefinierte Schüler-Accounts ───────────────────────────────────────────
USERS = {
    "schueler1": {"password": "pass123", "display": "Marco"},
    "schueler2": {"password": "pass123", "display": "Lena"},
    "schueler3": {"password": "pass123", "display": "David"},
    "schueler4": {"password": "pass123", "display": "Sarah"},
    "schueler5": {"password": "pass123", "display": "Tim"},
    "schueler6": {"password": "pass123", "display": "Nina"},
    "schueler7": {"password": "pass123", "display": "Finn"},
    "schueler8": {"password": "pass123", "display": "Jana"},
    "schueler9": {"password": "pass123", "display": "Leo"},
    "schueler10": {"password": "pass123", "display": "Mia"},
}

# ─── Bot Tokens (Schüler bekommen diesen Token für ihr Python Script) ─────────
BOT_TOKENS = {
    "token-schueler1-abc": "schueler1",
    "token-schueler2-def": "schueler2",
    "token-schueler3-ghi": "schueler3",
    "token-schueler4-jkl": "schueler4",
    "token-schueler5-mno": "schueler5",
    "token-schueler6-pqr": "schueler6",
    "token-schueler7-stu": "schueler7",
    "token-schueler8-vwx": "schueler8",
    "token-schueler9-yz1": "schueler9",
    "token-schueler10-234": "schueler10",
}

# ─── In-Memory Speicher ────────────────────────────────────────────────────────
messages = []          # Alle Chat-Nachrichten
pending_replies = {}   # Nachrichten die ein Bot noch beantworten muss
last_bot_response = {} # Rate limiting pro Bot
message_counter = 0

# ─── Auth Helper ──────────────────────────────────────────────────────────────
def get_user_from_token(token):
    return BOT_TOKENS.get(token)

def validate_user(username, password):
    user = USERS.get(username)
    if user and user["password"] == password:
        return user
    return None

# ─── Frontend ausliefern ──────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory("../frontend", filename)

# ─── REST API für Login ───────────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = validate_user(data.get("username"), data.get("password"))
    if user:
        # Bot Token für diesen User finden
        token = next((t for t, u in BOT_TOKENS.items() if u == data["username"]), None)
        return jsonify({
            "success": True,
            "display_name": user["display"],
            "username": data["username"],
            "bot_token": token
        })
    return jsonify({"success": False, "error": "Falscher Benutzername oder Passwort"}), 401

# ─── REST API für Bots (Schüler Scripts) ─────────────────────────────────────
@app.route("/api/messages", methods=["GET"])
def get_messages():
    """Bot holt Nachrichten die an ihn gerichtet sind"""
    token = request.headers.get("Authorization")
    username = get_user_from_token(token)
    if not username:
        return jsonify({"error": "Ungültiger Token"}), 401

    since = int(request.args.get("since", 0))
    # Nur Nachrichten die an diesen Bot gerichtet sind und noch nicht beantwortet wurden
    pending = [m for m in messages
               if m["id"] > since
               and m.get("to") == username
               and not m.get("bot_answered", False)
               and m.get("type") == "user"]
    return jsonify(pending)

@app.route("/api/send", methods=["POST"])
def bot_send():
    """Bot sendet eine Antwort"""
    global message_counter
    token = request.headers.get("Authorization")
    username = get_user_from_token(token)
    if not username:
        return jsonify({"error": "Ungültiger Token"}), 401

    # Rate limiting: max 1 Antwort alle 15 Sekunden
    now = time.time()
    if username in last_bot_response:
        if now - last_bot_response[username] < 15:
            return jsonify({"error": "Rate limit"}), 429
    last_bot_response[username] = now

    data = request.json
    message_counter += 1
    msg = {
        "id": message_counter,
        "type": "bot",
        "from": username,
        "bot_name": data.get("bot_name", f"{USERS[username]['display']}Bot"),
        "message": data.get("message", ""),
        "timestamp": int(time.time() * 1000),
        "display_name": USERS[username]["display"]
    }
    messages.append(msg)

    # Letzte 200 Nachrichten behalten
    if len(messages) > 200:
        messages.pop(0)

    # Echtzeit an alle Browser senden
    socketio.emit("new_message", msg)
    return jsonify({"success": True, "id": message_counter})

# ─── REST API für Browser (Schüler die eine Nachricht schicken) ───────────────
@app.route("/api/chat", methods=["POST"])
def chat_send():
    global message_counter
    data = request.json
    username = data.get("username")
    to = data.get("to")  # An welchen Schüler/Bot

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
        "to_display": USERS[to]["display"],
        "bot_answered": False
    }
    messages.append(msg)

    if len(messages) > 200:
        messages.pop(0)

    socketio.emit("new_message", msg)
    return jsonify({"success": True, "id": message_counter})

@app.route("/api/history", methods=["GET"])
def get_history():
    """Letzten 50 Nachrichten für Browser"""
    return jsonify(messages[-50:])

@app.route("/api/users", methods=["GET"])
def get_users():
    """Liste aller Schüler"""
    return jsonify([{"username": k, "display": v["display"]} for k, v in USERS.items()])

# ─── Socket.IO ────────────────────────────────────────────────────────────────
@socketio.on("connect")
def on_connect():
    emit("connected", {"status": "ok"})

if __name__ == "__main__":
    print("Chat Server läuft auf http://0.0.0.0:5000")
    print("\nBot Tokens für Schüler:")
    for token, user in BOT_TOKENS.items():
        print(f"  {USERS[user]['display']:10} → {token}")
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
