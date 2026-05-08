from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
import time
import os

app = Flask(__name__)
CORS(app, origins="*")

USERS = {
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

OPENAI_KEY = "sk-..."
AWS_LINK = "https://console.aws.amazon.com"

messages = []
message_counter = 0
custom_names = {}

def chat_key(a, b):
    return "-".join(sorted([a, b]))

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/keys")
def keys_page():
    return render_template_string('''
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Abraxas — Meine Keys</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
  :root { --bg:#0a1a1a; --surface:#0f2020; --surface2:#163030; --border:#1e4040; --accent:#00b4b4; --text:#e8f4f4; --muted:#5a9090; --radius:10px; --red:#ff5555; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'IBM Plex Sans',sans-serif; background:var(--bg); color:var(--text); min-height:100vh; display:flex; align-items:center; justify-content:center; padding:20px; }
  .box { background:var(--surface); border:1px solid var(--border); border-radius:16px; padding:40px; width:100%; max-width:480px; }
  .logo { display:flex; align-items:center; gap:10px; margin-bottom:32px; padding-bottom:20px; border-bottom:1px solid var(--border); }
  .logo-icon { width:32px; height:32px; background:var(--accent); border-radius:7px; display:flex; align-items:center; justify-content:center; font-size:16px; font-weight:700; color:#fff; font-family:'IBM Plex Mono',monospace; }
  .logo-text { font-family:'IBM Plex Mono',monospace; font-size:14px; color:var(--accent); letter-spacing:2px; }
  h1 { font-size:20px; margin-bottom:6px; }
  p { font-size:13px; color:var(--muted); margin-bottom:24px; }
  .field { margin-bottom:14px; }
  .field label { display:block; font-size:11px; font-family:'IBM Plex Mono',monospace; letter-spacing:1px; color:var(--muted); margin-bottom:6px; text-transform:uppercase; }
  .field input { width:100%; background:var(--surface2); border:1px solid var(--border); border-radius:var(--radius); padding:11px 14px; color:var(--text); font-family:'IBM Plex Mono',monospace; font-size:13px; outline:none; transition:border-color .2s; }
  .field input:focus { border-color:var(--accent); }
  .btn { width:100%; background:var(--accent); color:#fff; border:none; border-radius:var(--radius); padding:13px; font-family:'IBM Plex Mono',monospace; font-size:13px; font-weight:500; cursor:pointer; margin-top:8px; }
  .btn:hover { background:#00d4d4; }
  .error { font-size:12px; color:var(--red); margin-top:10px; display:none; }
  .result { display:none; margin-top:24px; border-top:1px solid var(--border); padding-top:24px; }
  .result h2 { font-size:16px; margin-bottom:16px; color:var(--accent); font-family:'IBM Plex Mono',monospace; }
  .key-item { background:var(--surface2); border:1px solid var(--border); border-radius:var(--radius); padding:14px; margin-bottom:10px; }
  .key-label { font-size:10px; font-family:'IBM Plex Mono',monospace; letter-spacing:1px; color:var(--muted); text-transform:uppercase; margin-bottom:6px; }
  .key-value { font-size:13px; font-family:'IBM Plex Mono',monospace; color:var(--accent); word-break:break-all; line-height:1.5; }
  .copy-btn { margin-top:8px; background:transparent; border:1px solid var(--border); color:var(--muted); border-radius:6px; padding:5px 10px; font-family:'IBM Plex Mono',monospace; font-size:11px; cursor:pointer; }
  .copy-btn:hover { border-color:var(--accent); color:var(--accent); }
  .aws-btn { display:block; width:100%; text-align:center; background:#ff9900; color:#000; border:none; border-radius:var(--radius); padding:13px; font-family:'IBM Plex Mono',monospace; font-size:13px; font-weight:500; cursor:pointer; text-decoration:none; margin-top:10px; }
  .chat-btn { display:block; width:100%; text-align:center; background:var(--surface2); color:var(--accent); border:1px solid var(--border); border-radius:var(--radius); padding:13px; font-family:'IBM Plex Mono',monospace; font-size:13px; cursor:pointer; text-decoration:none; margin-top:10px; }
</style>
</head>
<body>
<div class="box">
  <div class="logo">
    <div class="logo-icon">a</div>
    <div class="logo-text">abraxas</div>
  </div>
  <h1>Meine Keys</h1>
  <p>Melde dich an um deine Bot-ID und den OpenAI Key zu sehen</p>
  <div class="field"><label>Benutzername</label><input type="text" id="u" placeholder="schnuppi1" autocomplete="off"/></div>
  <div class="field"><label>Passwort</label><input type="password" id="p" placeholder="••••••••"/></div>
  <button class="btn" onclick="getKeys()">KEYS ANZEIGEN →</button>
  <div class="error" id="err">Falscher Benutzername oder Passwort</div>
  <div class="result" id="result">
    <h2>// Deine Infos</h2>
    <div class="key-item"><div class="key-label">Benutzername</div><div class="key-value" id="r-user">—</div></div>
    <div class="key-item"><div class="key-label">Bot-ID</div><div class="key-value" id="r-botid">—</div><button class="copy-btn" onclick="copy('r-botid', this)">Kopieren</button></div>
    <div class="key-item"><div class="key-label">OpenAI Key</div><div class="key-value" id="r-openai">—</div><button class="copy-btn" onclick="copy('r-openai', this)">Kopieren</button></div>
    <a class="aws-btn" href="{{ aws_link }}" target="_blank">☁️ AWS Console öffnen →</a>
    <a class="chat-btn" href="/" target="_blank">💬 Zur Chatplattform →</a>
  </div>
</div>
<script>
const S = window.location.origin;
async function getKeys() {
  const u = document.getElementById("u").value.trim();
  const p = document.getElementById("p").value;
  const err = document.getElementById("err");
  try {
    const r = await fetch(`${S}/api/login`, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({username:u, password:p})});
    const d = await r.json();
    if (d.success) {
      err.style.display = "none";
      const keysR = await fetch(`${S}/api/mykeys?username=${u}&password=${p}`);
      const keys = await keysR.json();
      document.getElementById("r-user").textContent = u;
      document.getElementById("r-botid").textContent = d.bot_id || "—";
      document.getElementById("r-openai").textContent = keys.openai_key || "—";
      document.getElementById("result").style.display = "block";
    } else { err.style.display = "block"; }
  } catch(e) { err.style.display = "block"; err.textContent = "Server nicht erreichbar"; }
}
function copy(id, btn) {
  navigator.clipboard.writeText(document.getElementById(id).textContent);
  btn.textContent = "✓ Kopiert!";
  setTimeout(() => btn.textContent = "Kopieren", 1500);
}
document.addEventListener("keydown", e => { if(e.key==="Enter") getKeys(); });
</script>
</body>
</html>
''', aws_link=AWS_LINK)

@app.route("/api/mykeys")
def my_keys():
    username = request.args.get("username")
    password = request.args.get("password")
    user = USERS.get(username)
    if not user or user["password"] != password:
        return jsonify({"error": "Unauthorized"}), 401
    if user["role"] != "schnuppi":
        return jsonify({"openai_key": "Nur für Schnuppis"})
    return jsonify({"openai_key": OPENAI_KEY})

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
        return jsonify({"success": True, "display_name": display, "username": data["username"], "bot_id": bot_id, "role": user["role"]})
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
    msg = {"id": message_counter, "chat_key": chat_key(username, to), "from": username, "to": to, "message": data.get("message", ""), "timestamp": int(time.time() * 1000), "display_name": display}
    messages.append(msg)
    if len(messages) > 500: messages.pop(0)
    return jsonify({"success": True, "id": message_counter})

@app.route("/api/history/<other>", methods=["GET"])
def get_history(other):
    username = request.args.get("me")
    if not username or username not in USERS or other not in USERS:
        return jsonify([])
    key = chat_key(username, other)
    return jsonify([m for m in messages if m.get("chat_key") == key][-50:])

@app.route("/api/poll/<other>", methods=["GET"])
def poll(other):
    username = request.args.get("me")
    since = int(request.args.get("since", 0))
    if not username or username not in USERS or other not in USERS:
        return jsonify([])
    key = chat_key(username, other)
    return jsonify([m for m in messages if m.get("chat_key") == key and m["id"] > since])

@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify([{"username": k, "display": custom_names.get(k, v["display"]), "role": v["role"]} for k, v in USERS.items()])

@app.route("/api/bot/messages", methods=["GET"])
def bot_messages():
    bot_id = request.headers.get("Authorization")
    username = BOT_IDS.get(bot_id)
    if not username:
        return jsonify({"error": "Ungültige ID"}), 401
    since = int(request.args.get("since", 0))
    return jsonify([m for m in messages if m["id"] > since and m.get("to") == username])

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
    msg = {"id": message_counter, "chat_key": chat_key(username, to), "from": username, "to": to, "message": data.get("message", ""), "timestamp": int(time.time() * 1000), "display_name": display}
    messages.append(msg)
    if len(messages) > 500: messages.pop(0)
    return jsonify({"success": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
