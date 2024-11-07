import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Initialize customtkinter theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Database setup
DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/24mca"
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


# User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    university_id = Column(String(15), unique=True)
    course = Column(String(50))
    university_email = Column(String(100))
    address = Column(String(150))
    phone_no = Column(String(15))
    password = Column(String(50))
    mst1_python = Column(Integer, default=0)
    mst1_network = Column(Integer, default=0)
    mst1_database = Column(Integer, default=0)
    mst1_web = Column(Integer, default=0)
    mst2_python = Column(Integer, default=0)
    mst2_network = Column(Integer, default=0)
    mst2_database = Column(Integer, default=0)
    mst2_web = Column(Integer, default=0)


Base.metadata.create_all(engine)


class UserManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("User Management System")
        self.root.geometry("600x400")
        self.show_login_page()

    def show_login_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        login_frame = ctk.CTkFrame(self.root, corner_radius=15)
        login_frame.pack(pady=20, padx=60, fill="both", expand=True)

        ctk.CTkLabel(login_frame, text="Adhar  ID").pack(pady=5)
        self.university_id_login = ctk.CTkEntry(login_frame)
        self.university_id_login.pack(pady=5)

        ctk.CTkLabel(login_frame, text="Password").pack(pady=5)
        self.password_login = ctk.CTkEntry(login_frame, show="*")
        self.password_login.pack(pady=5)

        ctk.CTkButton(login_frame, text="Login", command=self.login).pack(pady=10)
        ctk.CTkButton(login_frame, text="Sign Up", command=self.show_signup_page).pack()

    def show_signup_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        signup_frame = ctk.CTkFrame(self.root, corner_radius=15)
        signup_frame.pack(pady=20, padx=60, fill="both", expand=True)

        fields = ["Name", "Adhar Card number", "Course", "University Email", "Address", "Pancard number", "Passport size photo"]
        self.entries = {}

        for field in fields:
            ctk.CTkLabel(signup_frame, text=field).pack(pady=5)
            entry = ctk.CTkEntry(signup_frame, show="*" if field == "Password" else "")
            entry.pack(pady=5)
            self.entries[field] = entry

        ctk.CTkButton(signup_frame, text="Register", command=self.signup).pack(pady=10)
        ctk.CTkButton(signup_frame, text="Back to Login", command=self.show_login_page).pack()

    def signup(self):
        user_data = {field: entry.get() for field, entry in self.entries.items()}

        new_user = User(
            name=user_data["Name"],
            university_id=user_data["University ID"],
            course=user_data["Course"],
            university_email=user_data["University Email"],
            address=user_data["Address"],
            phone_no=user_data["Phone No"],
            password=user_data["Password"]
        )

        try:
            session.add(new_user)
            session.commit()
            messagebox.showinfo("Success", "Account created successfully.")
            self.show_login_page()
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", str(e))

    def login(self):
        university_id = self.university_id_login.get()
        password = self.password_login.get()

        user = session.query(User).filter_by(university_id=university_id, password=password).first()

        if user:
            self.current_user = user
            if user.mst1_python == 0:  # First-time login check
                self.show_mst_entry_page()
            else:
                self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid login credentials.")

    def show_mst_entry_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        mst_frame = ctk.CTkFrame(self.root, corner_radius=15)
        mst_frame.pack(pady=20, padx=60, fill="both", expand=True)

        ctk.CTkLabel(mst_frame, text="Enter 2nd class and 3rd class Marks (Max: 20)").pack(pady=5)

        subjects = ["python", "network", "database", "web"]
        self.mst1_entries = {}
        self.mst2_entries = {}

        for subject in subjects:
            ctk.CTkLabel(mst_frame, text=f"MST 1 {subject.capitalize()}").pack()
            entry_mst1 = ctk.CTkEntry(mst_frame)
            entry_mst1.pack(pady=5)
            self.mst1_entries[subject] = entry_mst1

            ctk.CTkLabel(mst_frame, text=f"MST 2 {subject.capitalize()}").pack()
            entry_mst2 = ctk.CTkEntry(mst_frame)
            entry_mst2.pack(pady=5)
            self.mst2_entries[subject] = entry_mst2

        ctk.CTkButton(mst_frame, text="Submit Marks", command=self.submit_mst_marks).pack(pady=10)

    def submit_mst_marks(self):
        try:
            for subject, entry in self.mst1_entries.items():
                mst1_score = int(entry.get())
                mst2_score = int(self.mst2_entries[subject].get())

                if not (0 <= mst1_score <= 20) or not (0 <= mst2_score <= 20):
                    messagebox.showerror("Error", "Marks should be between a and b.")
                    return

                setattr(self.current_user, f"mst1_{subject}", mst1_score)
                setattr(self.current_user, f"mst2_{subject}", mst2_score)

            session.commit()
            messagebox.showinfo("Success", "Marks submitted successfully.")
            self.show_dashboard()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid marks.")

    def show_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        dashboard_frame = ctk.CTkFrame(self.root, corner_radius=15)
        dashboard_frame.pack(pady=20, padx=60, fill="both", expand=True)

        user_info = f"Name: {self.current_user.name}\n" \
                    f"University ID: {self.current_user.university_id}\n" \
                    f"Course: {self.current_user.course}\n" \
                    f"Email: {self.current_user.university_email}\n" \
                    f"Address: {self.current_user.address}\n" \
                    f"Phone No: {self.current_user.phone_no}"

        ctk.CTkLabel(dashboard_frame, text=user_info).pack(pady=10)

        ctk.CTkButton(dashboard_frame, text="Logout", command=self.show_login_page).pack()

        self.show_marks_graph(dashboard_frame)

    def show_marks_graph(self, frame):
        subjects = ["Python", "Network", "Database", "Web"]
        mst1_marks = [
            self.current_user.mst1_python,
            self.current_user.mst1_network,
            self.current_user.mst1_database,
            self.current_user.mst1_web
        ]
        mst2_marks = [
            self.current_user.mst2_python,
            self.current_user.mst2_network,
            self.current_user.mst2_database,
            self.current_user.mst2_web
        ]

        figure = Figure(figsize=(5, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.bar(subjects, mst1_marks, label="MST 1", color="blue", alpha=0.6)
        ax.bar(subjects, mst2_marks, label="MST 2", color="red", alpha=0.6)
        ax.set_ylim([0, 20])
        ax.set_ylabel("Marks (Out of 20)")
        ax.legend()

        canvas = FigureCanvasTkAgg(figure, frame)
        canvas.get_tk_widget().pack(pady=10)


# Running the app
root = ctk.CTk()
app = UserManagementApp(root)
root.mainloop()
