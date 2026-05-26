import os
from datetime import datetime

FILE = "tasks.txt"

def load_tasks():
    tasks = []
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split("|")
                    if len(parts) == 3:
                        tasks.append({
                            "task": parts[0],
                            "status": parts[1],
                            "date": parts[2]
                        })
    return tasks

def save_tasks(tasks):
    with open(FILE, "w") as f:
        for t in tasks:
            f.write(f"{t['task']}|{t['status']}|{t['date']}\n")

def add_task(tasks):
    task = input("Enter task description: ").strip()
    if not task:
        print("Task cannot be empty.")
        return
    tasks.append({
        "task": task,
        "status": "Pending",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_tasks(tasks)
    print(f"✓ Task added: '{task}'")

def view_tasks(tasks):
    if not tasks:
        print("No tasks found.")
        return
    print(f"\n{'='*60}")
    print(f"  {'#':<4} {'Task':<28} {'Status':<12} {'Added'}")
    print(f"{'─'*60}")
    for i, t in enumerate(tasks, 1):
        status_icon = "✓" if t["status"] == "Done" else "○"
        print(f"  {i:<4} {t['task']:<28} {status_icon} {t['status']:<10} {t['date']}")
    print(f"{'='*60}")

def mark_done(tasks):
    view_tasks(tasks)
    if not tasks:
        return
    try:
        num = int(input("Enter task number to mark as done: "))
        if 1 <= num <= len(tasks):
            if tasks[num - 1]["status"] == "Done":
                print("Task is already marked as done.")
            else:
                tasks[num - 1]["status"] = "Done"
                save_tasks(tasks)
                print(f"✓ Task {num} marked as done!")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

def delete_task(tasks):
    view_tasks(tasks)
    if not tasks:
        return
    try:
        num = int(input("Enter task number to delete: "))
        if 1 <= num <= len(tasks):
            removed = tasks.pop(num - 1)
            save_tasks(tasks)
            print(f"✓ Task deleted: '{removed['task']}'")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

def show_summary(tasks):
    total = len(tasks)
    done = sum(1 for t in tasks if t["status"] == "Done")
    pending = total - done
    print(f"\n  Total Tasks : {total}")
    print(f"  Completed   : {done}")
    print(f"  Pending     : {pending}")

def main():
    print("=" * 40)
    print("      TO-DO LIST APPLICATION")
    print("=" * 40)
    tasks = load_tasks()

    while True:
        print("\nMenu:")
        print("  1. Add Task")
        print("  2. View All Tasks")
        print("  3. Mark Task as Done")
        print("  4. Delete Task")
        print("  5. Summary")
        print("  6. Exit")
        print("-" * 40)
        choice = input("Enter choice (1-6): ").strip()

        if choice == '1':
            add_task(tasks)
        elif choice == '2':
            view_tasks(tasks)
        elif choice == '3':
            mark_done(tasks)
        elif choice == '4':
            delete_task(tasks)
        elif choice == '5':
            show_summary(tasks)
        elif choice == '6':
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    main()
