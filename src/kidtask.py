
import json
from tkinter import *
from tkinter import messagebox

TASKS_FILE = "tasks.json"
WISHES_FILE = "wishes.json"

class User:
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

class Child(User):
    def __init__(self, id, username, level=1, points=0):
        super().__init__(id, username, "Child")
        self.level = level
        self.points = points

class Task:
    def __init__(self, id, title, description, points, status="PENDING"):
        self.id = id
        self.title = title
        self.description = description
        self.points = points
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "points": self.points,
            "status": self.status,
        }

    @staticmethod
    def from_dict(d):
        return Task(
            d["id"],
            d["title"],
            d.get("description", ""),
            d.get("points", 0),
            d.get("status", "PENDING"),
        )

class Wish:
    def __init__(self, id, name, minLevel, status="PENDING"):
        self.id = id
        self.name = name
        self.minLevel = minLevel
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "minLevel": self.minLevel,
            "status": self.status,
        }

    @staticmethod
    def from_dict(d):
        return Wish(
            d["id"],
            d["name"],
            d.get("minLevel", 1),
            d.get("status", "PENDING"),
        )

class StorageService:
    @staticmethod
    def load_json(path, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    @staticmethod
    def save_json(path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

class KidTaskGUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("KidTask")
        self.root.geometry("720x480")

        self.child = Child("c1", "Student A", level=1, points=0)
        self.tasks = []
        self.wishes = []
        self.load_data()

        self.header = Frame(self.root)
        self.header.pack(fill=X, pady=8)
        Label(self.header, text="KidTask Dashboard", font=("Arial", 18, "bold")).pack()

        btn_bar = Frame(self.root)
        btn_bar.pack(fill=X, pady=4)
        Button(btn_bar, text="View Tasks", width=20, command=self.show_tasks).pack(side=LEFT, padx=4)
        Button(btn_bar, text="View Wishes", width=20, command=self.show_wishes).pack(side=LEFT, padx=4)
        Button(btn_bar, text="View Progress", width=20, command=self.show_progress).pack(side=LEFT, padx=4)

        self.content = Frame(self.root)
        self.content.pack(fill=BOTH, expand=True)

        self.show_tasks()
        self.root.mainloop()

    def load_data(self):
        tasks_data = StorageService.load_json(TASKS_FILE, [])
        wishes_data = StorageService.load_json(WISHES_FILE, [])
        self.tasks = [Task.from_dict(t) for t in tasks_data]
        self.wishes = [Wish.from_dict(w) for w in wishes_data]

    def save_data(self):
        StorageService.save_json(TASKS_FILE, [t.to_dict() for t in self.tasks])
        StorageService.save_json(WISHES_FILE, [w.to_dict() for w in self.wishes])

    def next_id(self, prefix, items):
        max_num = 0
        for it in items:
            s = str(it.id)
            if s.startswith(prefix):
                tail = s[len(prefix):]
                if tail.isdigit():
                    max_num = max(max_num, int(tail))
        return f"{prefix}{max_num + 1}"

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_tasks(self):
        self.clear_content()

        top = Frame(self.content)
        top.pack(fill=X, pady=5)
        Label(top, text="Tasks", font=("Arial", 14, "bold")).pack(side=LEFT, padx=5)
        Button(top, text="Add Task", command=self.add_task_dialog).pack(side=RIGHT, padx=5)

        self.tasks_list = Listbox(self.content)
        self.tasks_list.pack(fill=BOTH, expand=True, padx=10, pady=5)

        for t in self.tasks:
            self.tasks_list.insert(END, f"[{t.status}] {t.title} - {t.points} pts")

        btn_frame = Frame(self.content)
        btn_frame.pack(pady=5)

        Button(
            btn_frame,
            text="Mark Selected as COMPLETED_PENDING_REVIEW",
            command=self.mark_task_completed,
            width=40
        ).pack(pady=3)

        Button(
            btn_frame,
            text="Approve Selected Task (APPROVED)",
            command=self.approve_task,
            width=40
        ).pack(pady=3)

    def add_task_dialog(self):
        win = Toplevel(self.root)
        win.title("Add Task")

        Label(win, text="Title:").grid(row=0, column=0, sticky="w", pady=2)
        e_title = Entry(win, width=30)
        e_title.grid(row=0, column=1, pady=2)

        Label(win, text="Description:").grid(row=1, column=0, sticky="w", pady=2)
        e_desc = Entry(win, width=30)
        e_desc.grid(row=1, column=1, pady=2)

        Label(win, text="Points:").grid(row=2, column=0, sticky="w", pady=2)
        e_points = Entry(win, width=10)
        e_points.grid(row=2, column=1, sticky="w", pady=2)

        def save():
            title = e_title.get().strip()
            desc = e_desc.get().strip()
            try:
                pts = int(e_points.get())
            except ValueError:
                messagebox.showerror("Error", "Points must be an integer.")
                return

            if not title:
                messagebox.showerror("Error", "Title is required.")
                return
            if pts < 0:
                messagebox.showerror("Error", "Points must be >= 0.")
                return

            new_id = self.next_id("t", self.tasks)
            task = Task(new_id, title, desc, pts, status="PENDING")
            self.tasks.append(task)
            self.save_data()
            self.show_tasks()
            win.destroy()

        Button(win, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=8)

    def mark_task_completed(self):
        selection = self.tasks_list.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a task first.")
            return

        task = self.tasks[selection[0]]

        if task.status == "APPROVED":
            messagebox.showinfo("Info", "Task is already approved.")
            return

        task.status = "COMPLETED_PENDING_REVIEW"
        self.save_data()
        self.show_tasks()
        messagebox.showinfo("Done", "Task marked as COMPLETED_PENDING_REVIEW (waiting for review).")

    def approve_task(self):
        selection = self.tasks_list.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a task first.")
            return

        task = self.tasks[selection[0]]

        if task.status != "COMPLETED_PENDING_REVIEW":
            messagebox.showinfo("Info", "Only COMPLETED_PENDING_REVIEW tasks can be approved.")
            return

        task.status = "APPROVED"
        self.save_data()
        self.show_tasks()
        messagebox.showinfo("Approved", f"Task approved! (+{task.points} pts)")

    def show_wishes(self):
        self.clear_content()

        top = Frame(self.content)
        top.pack(fill=X, pady=5)
        Label(top, text="Wishes", font=("Arial", 14, "bold")).pack(side=LEFT, padx=5)
        Button(top, text="Add Wish", command=self.add_wish_dialog).pack(side=RIGHT, padx=5)

        self.wishes_list = Listbox(self.content)
        self.wishes_list.pack(fill=BOTH, expand=True, padx=10, pady=5)

        for w in self.wishes:
            self.wishes_list.insert(END, f"[{w.status}] {w.name} (min level {w.minLevel})")

        btn_frame = Frame(self.content)
        btn_frame.pack(pady=5)

        Button(
            btn_frame,
            text="Redeem Selected Wish (if level is enough)",
            command=self.redeem_wish,
            width=40
        ).pack(pady=3)

    def add_wish_dialog(self):
        win = Toplevel(self.root)
        win.title("Add Wish")

        Label(win, text="Wish name:").grid(row=0, column=0, sticky="w", pady=2)
        e_name = Entry(win, width=30)
        e_name.grid(row=0, column=1, pady=2)

        Label(win, text="Min level:").grid(row=1, column=0, sticky="w", pady=2)
        e_lvl = Entry(win, width=10)
        e_lvl.grid(row=1, column=1, sticky="w", pady=2)

        def save():
            name = e_name.get().strip()
            if not name:
                messagebox.showerror("Error", "Wish name is required.")
                return

            try:
                min_level = int(e_lvl.get())
            except ValueError:
                messagebox.showerror("Error", "Min level must be an integer.")
                return

            if min_level < 1:
                messagebox.showerror("Error", "Min level must be >= 1.")
                return

            new_id = self.next_id("w", self.wishes)
            wish = Wish(new_id, name, min_level, status="PENDING")
            self.wishes.append(wish)
            self.save_data()
            self.show_wishes()
            win.destroy()

        Button(win, text="Save", command=save).grid(row=2, column=0, columnspan=2, pady=8)

    def refresh_child_progress(self):
        self.child.points = sum(t.points for t in self.tasks if t.status == "APPROVED")
        self.child.level = 1 + self.child.points // 50

    def redeem_wish(self):
        selection = self.wishes_list.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a wish first.")
            return

        self.refresh_child_progress()
        wish = self.wishes[selection[0]]

        if wish.status == "GRANTED":
            messagebox.showinfo("Info", "This wish is already granted.")
            return

        if self.child.level < wish.minLevel:
            messagebox.showwarning(
                "Not enough level",
                f"Your level is {self.child.level} but this wish requires level {wish.minLevel}."
            )
            return

        wish.status = "GRANTED"
        self.save_data()
        self.show_wishes()
        messagebox.showinfo("Granted", "Wish granted! 🎉")

    def show_progress(self):
        self.refresh_child_progress()
        self.clear_content()

        frame = Frame(self.content)
        frame.pack(fill=BOTH, expand=True, pady=40)

        Label(frame, text="Progress", font=("Arial", 16, "bold")).pack(pady=10)
        Label(frame, text=f"Total Points: {self.child.points}", font=("Arial", 14)).pack(pady=4)
        Label(frame, text=f"Level: {self.child.level}", font=("Arial", 14)).pack(pady=4)

        bar_outer = Frame(frame, width=400, height=24, bg="#dddddd")
        bar_outer.pack(pady=20)
        bar_outer.pack_propagate(False)

        remainder = self.child.points % 50
        pct = min(remainder / 50, 1.0)
        width = int(400 * pct)

        inner = Frame(bar_outer, width=width, bg="#4caf50")
        inner.pack(side=LEFT, fill=Y)

        Label(frame, text="Each 50 points increases the level by 1.", font=("Arial", 10, "italic")).pack()

        Button(frame, text="Back to Tasks", command=self.show_tasks).pack(pady=10)

if __name__ == "__main__":
    KidTaskGUI()
