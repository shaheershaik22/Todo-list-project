import os
from datetime import datetime

FILE = "tasks.txt"

def save_tasks(tasks):
    with open(FILE, "w") as f:
        for t in tasks:
            f.write(f"{t['task']}|{t['status']}|{t['date']}\n")

def load_tasks():
    tasks = []
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 3:
                    tasks.append({
                        "task": parts[0],
                        "status": parts[1],
                        "date": parts[2]
                    })
    return tasks

def add_task(tasks):
    task = input("Enter task: ").strip()
    if task == "":
        print("Task cannot be empty.")
        return
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tasks.append({"task": task, "status": "Pending", "date": date})
    save_tasks(tasks)
    print("Task added successfully.")

def view_tasks(tasks):
    if not tasks:
        print("No tasks found.")
        return

    for i, t in enumerate(tasks, 1):
        print(f"{i}. {t['task']} | {t['status']} | {t['date']}")

def mark_done(tasks):
    if not tasks:
        print("No tasks to mark.")
        return

    view_tasks(tasks)
    try:
        num = int(input("Enter task number to mark as done: "))
        if 1 <= num <= len(tasks):
            tasks[num - 1]["status"] = "Done"
            save_tasks(tasks)
            print("Task marked as done.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Enter a valid number.")

def delete_task(tasks):
    if not tasks:
        print("No tasks to delete.")
        return

    view_tasks(tasks)
    try:
        num = int(input("Enter task number to delete: "))
        if 1 <= num <= len(tasks):
            removed = tasks.pop(num - 1)
            save_tasks(tasks)
            print(f"Deleted task: {removed['task']}")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Enter a valid number.")

def summary(tasks):
    total = len(tasks)
    done = sum(1 for t in tasks if t["status"] == "Done")
    pending = total - done
    print(f"Total: {total}")
    print(f"Done: {done}")
    print(f"Pending: {pending}")

def main():
    tasks = load_tasks()

    while True:
        print("\n--- To-Do List ---")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Mark Task as Done")
        print("4. Delete Task")
        print("5. Summary")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            view_tasks(tasks)
        elif choice == "3":
            mark_done(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "5":
            summary(tasks)
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

main()