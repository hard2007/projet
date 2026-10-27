import tkinter as tk
from tkinter import ttk, messagebox

from services.auth_service import authenticate
from services.module_service import list_modules, list_teachers, list_students, add_module, update_student_group
from services.grade_service import (
    get_student_results, get_teacher_modules, get_students_for_module, upsert_grade
)


class MiniMassarApp:
    def __init__(self, root):
        self.root = root
        self.user = None
        self.root.title("Mini-Massar")
        self.root.geometry("1000x650")
        self.root.minsize(820, 540)
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.configure_styles()
        self.root.configure(background="#eef2f7")
        self.show_login()

    def configure_styles(self):
        self.style.configure("TFrame", background="#eef2f7")
        self.style.configure("TLabel", background="#eef2f7", foreground="#243247",
                             font=("Segoe UI", 10))
        self.style.configure("Card.TFrame", background="#ffffff")
        self.style.configure("Card.TLabel", background="#ffffff", foreground="#243247",
                             font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", background="#ffffff", foreground="#172b4d",
                             font=("Segoe UI", 26, "bold"))
        self.style.configure("Subtitle.TLabel", background="#ffffff", foreground="#718096",
                             font=("Segoe UI", 10))
        self.style.configure("Muted.TLabel", background="#ffffff", foreground="#718096",
                             font=("Segoe UI", 9))
        self.style.configure("Header.TFrame", background="#172b4d")
        self.style.configure("HeaderTitle.TLabel", background="#172b4d", foreground="#ffffff",
                             font=("Segoe UI", 18, "bold"))
        self.style.configure("HeaderMeta.TLabel", background="#172b4d", foreground="#cbd5e1",
                             font=("Segoe UI", 10))
        self.style.configure("TButton", background="#e2e8f0", foreground="#243247",
                             font=("Segoe UI", 10, "bold"), padding=(14, 9), borderwidth=0)
        self.style.map("TButton", background=[("active", "#cbd5e1")])
        self.style.configure("Accent.TButton", background="#087f8c", foreground="#ffffff",
                             font=("Segoe UI", 10, "bold"), padding=(16, 10), borderwidth=0)
        self.style.map("Accent.TButton", background=[("active", "#066875")])
        self.style.configure("TEntry", fieldbackground="#ffffff", foreground="#243247",
                             padding=8, borderwidth=1)
        self.style.configure("TCombobox", fieldbackground="#ffffff", foreground="#243247",
                             padding=6)
        self.style.configure("TNotebook", background="#eef2f7", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#e2e8f0", foreground="#526174",
                             padding=(18, 10), font=("Segoe UI", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", "#ffffff")],
                       foreground=[("selected", "#087f8c")])
        self.style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff",
                             foreground="#243247", rowheight=32, font=("Segoe UI", 10),
                             borderwidth=0)
        self.style.configure("Treeview.Heading", background="#e8eef5", foreground="#526174",
                             font=("Segoe UI", 9, "bold"), padding=(8, 9), relief="flat")
        self.style.map("Treeview.Heading", background=[("active", "#dbe5ef")])

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.user = None
        self.clear()
        outer = ttk.Frame(self.root, style="Card.TFrame", padding=36)
        outer.pack(expand=True)
        ttk.Label(outer, text="Mini-Massar", style="Title.TLabel").pack(pady=(0, 6))
        ttk.Label(outer, text="University student and grade management",
                  style="Subtitle.TLabel").pack(pady=(0, 24))
        form = ttk.Frame(outer, style="Card.TFrame")
        form.pack()
        ttk.Label(form, text="Username", style="Card.TLabel").grid(
            row=0, column=0, sticky="w", padx=8, pady=8)
        username = ttk.Entry(form, width=32)
        username.grid(row=0, column=1, padx=8, pady=8)
        ttk.Label(form, text="Password", style="Card.TLabel").grid(
            row=1, column=0, sticky="w", padx=8, pady=8)
        password = ttk.Entry(form, width=32, show="*")
        password.grid(row=1, column=1, padx=8, pady=8)

        def do_login(_event=None):
            try:
                user = authenticate(username.get(), password.get())
            except Exception as exc:
                messagebox.showerror("Login error", str(exc))
                return
            if user is None:
                messagebox.showerror("Login failed", "Incorrect username or password.")
                return
            self.user = user
            if user["role"] == "student":
                self.show_student_dashboard()
            else:
                self.show_teacher_dashboard()

        ttk.Button(outer, text="Log in", style="Accent.TButton",
                   command=do_login).pack(pady=14, fill="x")
        password.bind("<Return>", do_login)
        username.focus_set()
        ttk.Label(outer, text="Demo accounts must be created before the first login.",
                  style="Muted.TLabel").pack(pady=(10, 0))

    def dashboard_header(self, title):
        header = ttk.Frame(self.root, style="Header.TFrame", padding=(22, 16))
        header.pack(fill="x")
        ttk.Label(header, text=title, style="HeaderTitle.TLabel").pack(side="left")
        ttk.Label(header, text=f"{self.user['full_name']} · {self.user['role'].title()}",
                  style="HeaderMeta.TLabel").pack(side="left", padx=20)
        ttk.Button(header, text="Log out", command=self.show_login).pack(side="right")

    def show_student_dashboard(self):
        self.clear()
        self.dashboard_header("Student dashboard")
        body = ttk.Frame(self.root, padding=18)
        body.pack(fill="both", expand=True)
        group = self.user.get("group_name") or "Not assigned"
        ttk.Label(body, text=f"Group: {group}",
                  font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))
        ttk.Label(body, text="Your grades and module results",
                  foreground="#718096").pack(anchor="w")
        columns = ("module", "teacher", "coefficient", "coursework", "exam", "average")
        tree = ttk.Treeview(body, columns=columns, show="headings", height=15)
        headings = {
            "module": "Module", "teacher": "Teacher", "coefficient": "Coeff.",
            "coursework": "Coursework /20", "exam": "Exam /20", "average": "Module average /20"
        }
        widths = {"module": 190, "teacher": 180, "coefficient": 75, "coursework": 120, "exam": 100, "average": 145}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="center")
        tree.pack(fill="both", expand=True, pady=10)
        try:
            result = get_student_results(self.user["user_id"])
            for row in result["grades"]:
                fmt = lambda x: "—" if x is None else f"{x:.2f}"
                tree.insert("", "end", values=(
                    row["module_name"], row["teacher_name"], row["coefficient"],
                    fmt(row["coursework_mark"]), fmt(row["exam_mark"]), fmt(row["module_average"])
                ))
            avg = result["semester_average"]
            average_text = "Not available yet" if avg is None else f"{avg:.2f} / 20"
            ttk.Label(body, text=f"Weighted semester average: {average_text}",
                      font=("Segoe UI", 12, "bold"),
                      foreground="#087f8c").pack(anchor="e", pady=6)
        except Exception as exc:
            messagebox.showerror("Results error", str(exc))

    def show_teacher_dashboard(self):
        self.clear()
        self.dashboard_header("Teacher dashboard")
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=14, pady=14)
        grades_tab = ttk.Frame(notebook, padding=12)
        modules_tab = ttk.Frame(notebook, padding=12)
        students_tab = ttk.Frame(notebook, padding=12)
        notebook.add(grades_tab, text="Enter grades")
        notebook.add(modules_tab, text="Modules")
        notebook.add(students_tab, text="Students and groups")
        self.build_grade_tab(grades_tab)
        self.build_modules_tab(modules_tab)
        self.build_students_tab(students_tab)

    def build_grade_tab(self, parent):
        try:
            modules = get_teacher_modules(self.user["user_id"])
        except Exception as exc:
            messagebox.showerror("Modules error", str(exc))
            return
        if not modules:
            ttk.Label(parent, text="No modules are assigned to this teacher yet.").pack(anchor="w")
            return
        module_by_label = {f"{m['module_name']} (coefficient {m['coefficient']})": m for m in modules}
        module_var = tk.StringVar(value=next(iter(module_by_label)))
        ttk.Label(parent, text="Module").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        module_combo = ttk.Combobox(parent, textvariable=module_var, values=list(module_by_label), state="readonly", width=42)
        module_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        students = list_students()
        student_by_label = {f"{s['full_name']} ({s['username']}) — {s['group_name'] or 'No group'}": s for s in students}
        student_var = tk.StringVar(value=next(iter(student_by_label), ""))
        ttk.Label(parent, text="Student").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        student_combo = ttk.Combobox(parent, textvariable=student_var, values=list(student_by_label), state="readonly", width=55)
        student_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(parent, text="Coursework mark /20").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        coursework = ttk.Entry(parent, width=20)
        coursework.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(parent, text="Exam mark /20").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        exam = ttk.Entry(parent, width=20)
        exam.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        status = ttk.Label(parent, text="")
        status.grid(row=5, column=0, columnspan=2, sticky="w", pady=8)

        def save_grade():
            try:
                module = module_by_label[module_var.get()]
                student = student_by_label[student_var.get()]
                upsert_grade(student["user_id"], module["module_id"], coursework.get(), exam.get(), self.user["user_id"])
                status.config(text="Grade saved successfully.")
            except Exception as exc:
                messagebox.showerror("Could not save grade", str(exc))

        ttk.Button(parent, text="Save grade", style="Accent.TButton",
                   command=save_grade).grid(row=4, column=1, sticky="w", padx=5, pady=12)
        ttk.Label(parent, text="Both marks must be between 0 and 20. Leave one blank if not yet graded.",
                  foreground="#718096").grid(row=6, column=0, columnspan=2, sticky="w", pady=8)

    def build_modules_tab(self, parent):
        ttk.Label(parent, text="Your assigned modules").pack(anchor="w", pady=(0, 8))
        columns = ("name", "coefficient")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=8)
        tree.heading("name", text="Module")
        tree.heading("coefficient", text="Coefficient")
        tree.column("name", width=300)
        tree.column("coefficient", width=120, anchor="center")
        tree.pack(fill="x")
        for module in get_teacher_modules(self.user["user_id"]):
            tree.insert("", "end", values=(module["module_name"], module["coefficient"]))

    def build_students_tab(self, parent):
        ttk.Label(parent, text="Student roster and group assignment").pack(anchor="w", pady=(0, 8))
        columns = ("id", "name", "username", "group")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        for col, label, width in [("id", "ID", 60), ("name", "Full name", 220),
                                  ("username", "Username", 140), ("group", "Group", 120)]:
            tree.heading(col, text=label)
            tree.column(col, width=width)
        tree.pack(fill="both", expand=True)
        students = list_students()
        for s in students:
            tree.insert("", "end", iid=str(s["user_id"]),
                        values=(s["user_id"], s["full_name"], s["username"], s["group_name"] or ""))
        controls = ttk.Frame(parent)
        controls.pack(fill="x", pady=10)
        group_var = tk.StringVar()
        ttk.Label(controls, text="New group for selected student:").pack(side="left")
        ttk.Entry(controls, textvariable=group_var, width=18).pack(side="left", padx=8)

        def assign_group():
            selected = tree.selection()
            if not selected:
                messagebox.showinfo("Select student", "Select a student row first.")
                return
            try:
                student_id = int(selected[0])
                update_student_group(student_id, group_var.get())
                tree.set(selected[0], "group", group_var.get().strip())
                messagebox.showinfo("Updated", "Student group updated.")
            except Exception as exc:
                messagebox.showerror("Update failed", str(exc))

        ttk.Button(controls, text="Assign group", style="Accent.TButton",
                   command=assign_group).pack(side="left")

    def build_modules_admin_tab(self, parent):
        # Kept as a helper for future extension; modules are initially assigned by setup script.
        pass


def create_main_window():
    root = tk.Tk()
    MiniMassarApp(root)
    return root
