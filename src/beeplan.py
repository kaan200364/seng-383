
import tkinter as tk
from tkinter import ttk, messagebox

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
HOURS = ["09:20", "10:20", "11:20", "12:20", "13:20", "14:20", "15:20", "16:20"]

class Instructor:
    def __init__(self, name):
        self.name = name
        self.daily_hours = {day: 0 for day in DAYS}

class Course:
    def __init__(self, code, year, hours, instructor):
        self.code = code
        self.year = year
        self.hours = hours
        self.instructor = instructor

class BeePlanScheduler:
    def __init__(self, courses):
        self.courses = courses
        self.schedule = {}
        self.unplaced = []

    def generate(self):
        self.schedule.clear()
        self.unplaced.clear()

        for c in self.courses:
            c.instructor.daily_hours = {day: 0 for day in DAYS}

        for course in self.courses:
            placed_hours = 0

            for day in DAYS:
                for hour in HOURS:
                    if placed_hours == course.hours:
                        break

                    key = (day, hour, course.year)

                    if key in self.schedule:
                        continue

                    if day == "Friday" and hour in ["13:20", "14:20"]:
                        continue

                    if course.instructor.daily_hours[day] >= 4:
                        continue

                    instructor_busy = any(
                        d == day and h == hour and scheduled_course.instructor == course.instructor
                        for (d, h, y), scheduled_course in self.schedule.items()
                    )
                    if instructor_busy:
                        continue

                    self.schedule[key] = course
                    course.instructor.daily_hours[day] += 1
                    placed_hours += 1

                if placed_hours == course.hours:
                    break

            if placed_hours < course.hours:
                self.unplaced.append((course, course.hours - placed_hours))

    def get_cell(self, day, hour, year):
        course = self.schedule.get((day, hour, year))
        if course:
            return f"{course.code}\n{course.instructor.name}"
        return ""

class BeePlanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BeePlan – Weekly Course Schedule")
        self.root.geometry("1100x600")

        title = tk.Label(
            root,
            text="BeePlan – Çankaya University Course Scheduling System",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=10)

        btn = tk.Button(
            root,
            text="Generate Schedule",
            font=("Arial", 12),
            command=self.generate_schedule
        )
        btn.pack(pady=5)

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(expand=True, fill="both")

        self.setup_scheduler()
        self.create_year_tabs()

    def setup_scheduler(self):
        h1 = Instructor("Ahmet Hoca")
        h2 = Instructor("Ayşe Hoca")
        h3 = Instructor("Mehmet Hoca")
        h4 = Instructor("Can Hoca")

        self.courses = [
            Course("PHYS131", 1, 3, h1),
            Course("MATH157", 1, 4, h2),
            Course("SENG101", 1, 3, h3),
            Course("CHEM101", 1, 2, h4),

            Course("SENG201", 2, 3, h1),
            Course("MATH255", 2, 3, h2),
            Course("PHYS211", 2, 3, h3),
            Course("SENG203", 2, 2, h4),

            Course("SENG311", 3, 3, h1),
            Course("SENG315", 3, 3, h3),
            Course("SENG321", 3, 3, h2),
            Course("SENG399", 3, 2, h4),

            Course("SENG401", 4, 3, h2),
            Course("SENG411", 4, 3, h1),
            Course("SENG499", 4, 2, h3),
            Course("SENG497", 4, 2, h4),
        ]

        self.scheduler = BeePlanScheduler(self.courses)

    def create_year_tabs(self):
        self.tables = {}

        for year in [1, 2, 3, 4]:
            frame = tk.Frame(self.tabs)
            self.tabs.add(frame, text=f"Year {year}")

            table = {"frame": frame, "cells": {}}

            tk.Label(frame, text="Hour / Day", borderwidth=1, relief="solid", width=12).grid(row=0, column=0)
            for c, day in enumerate(DAYS):
                tk.Label(frame, text=day, borderwidth=1, relief="solid", width=20).grid(row=0, column=c + 1)

            for r, hour in enumerate(HOURS):
                tk.Label(frame, text=hour, borderwidth=1, relief="solid", width=12).grid(row=r + 1, column=0)
                for c, day in enumerate(DAYS):
                    lbl = tk.Label(
                        frame,
                        text="",
                        borderwidth=1,
                        relief="solid",
                        width=20,
                        height=3,
                        justify="center"
                    )
                    lbl.grid(row=r + 1, column=c + 1)
                    table["cells"][(day, hour)] = lbl

            self.tables[year] = table

    def generate_schedule(self):
        self.scheduler.generate()

        for year, table in self.tables.items():
            for (day, hour), lbl in table["cells"].items():
                lbl.config(text=self.scheduler.get_cell(day, hour, year))

        if self.scheduler.unplaced:
            lines = []
            for course, rem in self.scheduler.unplaced:
                lines.append(f"{course.code} (Year {course.year}) -> {rem} hour(s) could not be placed")
            messagebox.showwarning("Warning", "Some courses could not be fully placed:\n\n" + "\n".join(lines))
        else:
            messagebox.showinfo("OK", "Schedule generated successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BeePlanGUI(root)
    root.mainloop()
