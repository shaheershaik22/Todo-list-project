import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

DATA_FILE = "tasks.txt"
HOST = "127.0.0.1"
PORT = 8000


def load_tasks():
    tasks = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) == 3:
                    tasks.append(
                        {
                            "task": parts[0],
                            "status": parts[1],
                            "date": parts[2],
                        }
                    )
    return tasks


def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        for task in tasks:
            f.write(f"{task['task']}|{task['status']}|{task['date']}\n")


def add_task(task_text):
    task_text = task_text.strip()
    if not task_text:
        return {"ok": False, "error": "Task cannot be empty."}

    tasks = load_tasks()
    tasks.append(
        {
            "task": task_text,
            "status": "Pending",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    save_tasks(tasks)
    return {"ok": True, "tasks": tasks}


def mark_done(index):
    tasks = load_tasks()
    if not 0 <= index < len(tasks):
        return {"ok": False, "error": "Invalid task."}

    tasks[index]["status"] = "Done"
    save_tasks(tasks)
    return {"ok": True, "tasks": tasks}


def delete_task(index):
    tasks = load_tasks()
    if not 0 <= index < len(tasks):
        return {"ok": False, "error": "Invalid task."}

    tasks.pop(index)
    save_tasks(tasks)
    return {"ok": True, "tasks": tasks}


def summary(tasks):
    total = len(tasks)
    done = sum(1 for task in tasks if task["status"] == "Done")
    pending = total - done
    return {"total": total, "done": done, "pending": pending}


HTML = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>To-Do Web App</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Arial, sans-serif;
      background: #f3f4f6;
      color: #111827;
    }
    body {
      margin: 0;
      padding: 24px;
    }
    .container {
      max-width: 900px;
      margin: 0 auto;
      background: white;
      border-radius: 18px;
      padding: 24px;
      box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    }
    h1 {
      margin-top: 0;
      font-size: 1.8rem;
    }
    .topbar {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 20px;
    }
    #taskInput {
      flex: 1;
      min-width: 240px;
      padding: 12px 14px;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      font-size: 1rem;
    }
    button {
      border: 0;
      border-radius: 10px;
      padding: 12px 16px;
      font-size: 1rem;
      cursor: pointer;
      font-weight: 600;
    }
    #addBtn {
      background: #2563eb;
      color: white;
    }
    .summary {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }
    .summary-card {
      background: #eff6ff;
      border-radius: 12px;
      padding: 14px;
    }
    .summary-card strong {
      display: block;
      font-size: 1.4rem;
      margin-top: 6px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th, td {
      text-align: left;
      padding: 12px 10px;
      border-bottom: 1px solid #e5e7eb;
      vertical-align: top;
    }
    th {
      font-size: 0.92rem;
      color: #4b5563;
    }
    .status-pending {
      color: #b45309;
      font-weight: 700;
    }
    .status-done {
      color: #047857;
      font-weight: 700;
    }
    .actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .mark-btn {
      background: #047857;
      color: white;
    }
    .delete-btn {
      background: #dc2626;
      color: white;
    }
    .empty {
      color: #6b7280;
      padding: 18px 0;
    }
    .message {
      margin-top: 14px;
      min-height: 1.5rem;
      color: #b45309;
    }
  </style>
</head>
<body>
  <div class=\"container\">
    <h1>To-Do Web App</h1>
    <p>Add, complete, and remove tasks from your browser.</p>

    <form id=\"taskForm\" class=\"topbar\">
      <input id=\"taskInput\" type=\"text\" placeholder=\"Enter a new task\" autocomplete=\"off\" required />
      <button id=\"addBtn\" type=\"submit\">Add Task</button>
    </form>

    <div id=\"summary\" class=\"summary\"></div>
    <div class=\"message\" id=\"message\"></div>

    <table>
      <thead>
        <tr>
          <th>Task</th>
          <th>Status</th>
          <th>Added</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody id=\"taskList\"></tbody>
    </table>
  </div>

  <script>
    const taskForm = document.getElementById('taskForm');
    const taskInput = document.getElementById('taskInput');
    const taskList = document.getElementById('taskList');
    const summary = document.getElementById('summary');
    const message = document.getElementById('message');

    async function apiRequest(payload) {
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Request failed.');
      }
      return data;
    }

    function renderSummary(data) {
      summary.innerHTML = `
        <div class=\"summary-card\">Total <strong>${data.total}</strong></div>
        <div class=\"summary-card\">Done <strong>${data.done}</strong></div>
        <div class=\"summary-card\">Pending <strong>${data.pending}</strong></div>
      `;
    }

    function renderTasks(tasks) {
      if (!tasks.length) {
        taskList.innerHTML = '<tr><td colspan=\"4\" class=\"empty\">No tasks yet. Add one to get started.</td></tr>';
        return;
      }

      taskList.innerHTML = tasks.map((task, index) => `
        <tr>
          <td>${escapeHtml(task.task)}</td>
          <td class=\"${task.status === 'Done' ? 'status-done' : 'status-pending'}\">${task.status}</td>
          <td>${escapeHtml(task.date)}</td>
          <td>
            <div class=\"actions\">
              ${task.status !== 'Done' ? `<button class=\"mark-btn\" data-index=\"${index}\">Mark Done</button>` : ''}
              <button class=\"delete-btn\" data-index=\"${index}\">Delete</button>
            </div>
          </td>
        </tr>
      `).join('');
    }

    function escapeHtml(value) {
      return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    async function refresh() {
      const response = await fetch('/api/tasks');
      const tasks = await response.json();
      renderTasks(tasks);
      renderSummary({
        total: tasks.length,
        done: tasks.filter(task => task.status === 'Done').length,
        pending: tasks.filter(task => task.status !== 'Done').length
      });
      message.textContent = '';
    }

    taskForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const task = taskInput.value;
      try {
        await apiRequest({ action: 'add', task });
        taskInput.value = '';
        message.textContent = 'Task added successfully.';
        await refresh();
      } catch (error) {
        message.textContent = error.message;
      }
    });

    taskList.addEventListener('click', async (event) => {
      const target = event.target;
      if (!(target instanceof HTMLElement)) {
        return;
      }

      const index = Number(target.dataset.index);
      if (Number.isNaN(index)) {
        return;
      }

      try {
        if (target.classList.contains('mark-btn')) {
          await apiRequest({ action: 'done', index });
          message.textContent = 'Task marked as done.';
        } else if (target.classList.contains('delete-btn')) {
          await apiRequest({ action: 'delete', index });
          message.textContent = 'Task deleted.';
        }
        await refresh();
      } catch (error) {
        message.textContent = error.message;
      }
    });

    refresh();
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode("utf-8"))
            return

        if parsed.path == "/api/tasks":
            tasks = load_tasks()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(tasks).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/tasks":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8")

        try:
            payload = json.loads(raw_body) if raw_body else {}
        except json.JSONDecodeError:
            payload = {}

        action = payload.get("action")

        try:
            if action == "add":
                result = add_task(payload.get("task", ""))
            elif action == "done":
                result = mark_done(int(payload.get("index", -1)))
            elif action == "delete":
                result = delete_task(int(payload.get("index", -1)))
            else:
                result = {"ok": False, "error": "Unknown action."}
        except ValueError:
            result = {"ok": False, "error": "Invalid task index."}

        response = json.dumps(result)
        if result.get("ok"):
            self.send_response(200)
        else:
            self.send_response(400)

        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), Handler)
    print(f"Web app running at http://{HOST}:{PORT}")
    server.serve_forever()
