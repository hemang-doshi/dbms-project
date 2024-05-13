import pymysql
import tkinter as tk
from tkinter import ttk, messagebox

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'dbsproj'
}

def create_connection():
    try:
        conn = pymysql.connect(**db_config)
        return conn
    except pymysql.Error as e:
        messagebox.showerror("Error", f"Failed to connect to database: {e}")
        return None

def execute_query(conn, query, params=None):
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            conn.commit()
            print("Query executed and committed successfully.")
    except pymysql.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        print(f"An error occurred: {e}")

def execute_read_query(conn, query, params=None):
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall()
    except pymysql.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
        return []

def login_user(username, password, user_type):
    conn = create_connection()
    if conn:
        if user_type == 'student':
            query = "SELECT student_id FROM student_users WHERE username=%s AND password=%s"
        else:
            query = "SELECT professor_id FROM admin_users WHERE username=%s AND password=%s"

        result = execute_read_query(conn, query, (username, password))
        if result:
            return result[0][0]  # Return ID of the user
        else:
            messagebox.showinfo("Login Failed", "Invalid username or password")
    return None

def show_student_interface(student_id):
    conn = create_connection()
    if conn:
        # Fetch student information
        student_info_query = "SELECT * FROM Students WHERE student_id=%s"
        student_info = execute_read_query(conn, student_info_query, (student_id,))

        if student_info:
            # Fetch subject-wise attendance for the student
            attendance_query = """
                SELECT Subjects.subject_name, Attendance.date, Attendance.status
                FROM Attendance
                INNER JOIN Subjects ON Attendance.subject_id = Subjects.subject_id
                WHERE Attendance.student_id = %s
            """
            attendance_data = execute_read_query(conn, attendance_query, (student_id,))

            # Display student information and attendance details
            student_info_window = tk.Toplevel()
            student_info_window.title("Student Information")
            ttk.Label(student_info_window, text=f"Student ID: {student_info[0][0]}").pack()
            ttk.Label(student_info_window, text=f"Name: {student_info[0][1]} {student_info[0][2]}").pack()
            ttk.Label(student_info_window, text=f"DOB: {student_info[0][3]}").pack()
            ttk.Label(student_info_window, text=f"Gender: {student_info[0][4]}").pack()
            ttk.Label(student_info_window, text=f"Address: {student_info[0][5]}").pack()
            ttk.Label(student_info_window, text=f"Email: {student_info[0][6]}").pack()
            ttk.Label(student_info_window, text=f"Parent ID: {student_info[0][7]}").pack()

            # Display attendance details
            ttk.Label(student_info_window, text="Attendance Details", font=("Helvetica", 14, "bold")).pack(pady=10)
            if attendance_data:
                for subject, date, status in attendance_data:
                    ttk.Label(student_info_window, text=f"Subject: {subject} | Date: {date} | Status: {status}").pack()
            else:
                ttk.Label(student_info_window, text="No attendance records found.").pack()
        else:
            messagebox.showinfo("Student Not Found", "Student information not found.")

def add_student(student_details):
    conn = create_connection()
    if conn:
        query = """
            INSERT INTO Students (student_id, first_name, last_name, date_of_birth, gender, address, phone_number, email, parent_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        execute_query(conn, query, student_details)
        messagebox.showinfo("Success", "Student added successfully")
        print("Added student:", student_details)
        conn.commit()
        conn.close()
    else:
        print("Failed to connect to the database.")


def add_professor(professor_details):
    conn = create_connection()
    if conn:
        query = """
            INSERT INTO Professors (professor_id, professor_first_name, professor_last_name, professor_email, professor_phone_number)
            VALUES (%s, %s, %s, %s, %s);
        """
        execute_query(conn, query, professor_details)
        messagebox.showinfo("Success", "Professor added successfully")
        conn.close()


def add_subject(subject_details):
    conn = create_connection()
    if conn:
        query = """
            INSERT INTO Subjects (subject_name, professor_id)
            VALUES (%s, %s);
        """
        execute_query(conn, query, subject_details)
        messagebox.showinfo("Success", "Subject added successfully")
        conn.close()

def record_attendance(attendance_details):
    conn = create_connection()
    if conn:
        query = """
            INSERT INTO Attendance (student_id, subject_id, date, status)
            VALUES (%s, %s, %s, %s);
        """
        execute_query(conn, query, attendance_details)
        messagebox.showinfo("Success", "Attendance recorded successfully")
        conn.close()

# Continue the rest of your program here as previously defined

def show_admin_interface(professor_id):
    conn = create_connection()
    if conn:
        admin_window = tk.Toplevel()
        admin_window.title("Admin Dashboard")

        tab_control = ttk.Notebook(admin_window)
        students_tab = ttk.Frame(tab_control)
        professors_tab = ttk.Frame(tab_control)
        subjects_tab = ttk.Frame(tab_control)
        attendance_tab = ttk.Frame(tab_control)
        check_attendance_tab = ttk.Frame(tab_control)  # New tab for checking attendance
        tab_control.add(students_tab, text='Students')
        tab_control.add(professors_tab, text='Professors')
        tab_control.add(subjects_tab, text='Subjects')
        tab_control.add(attendance_tab, text='Attendance')
        tab_control.add(check_attendance_tab, text='Check Attendance')  # Add the new tab
        tab_control.pack(expand=1, fill='both')

        setup_students_tab(students_tab)
        setup_professors_tab(professors_tab)
        setup_subjects_tab(subjects_tab)
        setup_attendance_tab(attendance_tab)
        setup_check_attendance_tab(check_attendance_tab)  # Setup the new tab

def setup_check_attendance_tab(tab):
    ttk.Label(tab, text="Check Attendance").grid(column=0, row=0, padx=10, pady=10)

    ttk.Label(tab, text="Enter Student ID:").grid(column=0, row=1)
    student_id_entry = ttk.Entry(tab)
    student_id_entry.grid(column=1, row=1)

    result_label = ttk.Label(tab, text="")
    result_label.grid(column=0, row=2, columnspan=2)

    def calculate_attendance():
        student_id = student_id_entry.get()
        if student_id:
            attendance_percentage = get_attendance_percentage(student_id)
            result_label.config(text=attendance_percentage)

    ttk.Button(tab, text="Check Attendance", command=calculate_attendance).grid(column=0, row=3, columnspan=2)

def get_attendance_percentage(student_id):
    conn = create_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("CALL CalculateAttendancePercentage(%s)", (student_id,))
                result = cur.fetchone()
                if result:
                    return result[0]  # Attendance percentage
                else:
                    return "Attendance data not found."
        except pymysql.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            return "Error fetching attendance data."
        finally:
            conn.close()
    else:
        return "Failed to connect to the database."


def setup_students_tab(tab):
    ttk.Label(tab, text="Student Management").grid(column=0, row=0, padx=10, pady=10)
    
    ttk.Label(tab, text="Student ID:").grid(column=0, row=1)
    student_id_entry = ttk.Entry(tab)
    student_id_entry.grid(column=1, row=1)

    ttk.Label(tab, text="First Name:").grid(column=0, row=2)
    first_name_entry = ttk.Entry(tab)
    first_name_entry.grid(column=1, row=2)

    ttk.Label(tab, text="Last Name:").grid(column=0, row=3)
    last_name_entry = ttk.Entry(tab)
    last_name_entry.grid(column=1, row=3)

    ttk.Label(tab, text="DOB (YYYY-MM-DD):").grid(column=0, row=4)
    dob_entry = ttk.Entry(tab)
    dob_entry.grid(column=1, row=4)

    ttk.Label(tab, text="Gender (M/F):").grid(column=0, row=5)
    gender_combobox = ttk.Combobox(tab, values=["M", "F"])
    gender_combobox.grid(column=1, row=5)
    ttk.Label(tab, text="Gender:").grid(column=2, row=5)

    ttk.Label(tab, text="Address:").grid(column=0, row=6)
    address_entry = ttk.Entry(tab)
    address_entry.grid(column=1, row=6)

    ttk.Label(tab, text="Email:").grid(column=0, row=7)
    email_entry = ttk.Entry(tab)
    email_entry.grid(column=1, row=7)

    ttk.Label(tab, text="Phone Number:").grid(column=0, row=8)
    phone_entry = ttk.Entry(tab)
    phone_entry.grid(column=1, row=8)

    ttk.Label(tab, text="Parent ID:").grid(column=0, row=9)
    parent_id_entry = ttk.Entry(tab)
    parent_id_entry.grid(column=1, row=9)

    ttk.Button(tab, text="Add Student", command=lambda: add_student([
    student_id_entry.get(),
    first_name_entry.get(),
    last_name_entry.get(),
    dob_entry.get(),
    "Male" if gender_combobox.get() == "M" else "Female",  # Convert "M" to "Male" and "F" to "Female"
    address_entry.get(),
    phone_entry.get(),  # Add phone number to the parameters
    email_entry.get(),
    parent_id_entry.get(),
])).grid(column=0, row=10)
    

def setup_professors_tab(tab):
    ttk.Label(tab, text="Professor Management").grid(column=0, row=0, padx=10, pady=10)
    
    ttk.Label(tab, text="Professor ID:").grid(column=0, row=1)
    professor_id_entry = ttk.Entry(tab)
    professor_id_entry.grid(column=1, row=1)

    ttk.Label(tab, text="First Name:").grid(column=0, row=2)
    first_name_entry = ttk.Entry(tab)
    first_name_entry.grid(column=1, row=2)

    ttk.Label(tab, text="Last Name:").grid(column=0, row=3)
    last_name_entry = ttk.Entry(tab)
    last_name_entry.grid(column=1, row=3)

    ttk.Label(tab, text="Email:").grid(column=0, row=4)
    email_entry = ttk.Entry(tab)
    email_entry.grid(column=1, row=4)

    ttk.Label(tab, text="Phone Number:").grid(column=0, row=5)
    phone_entry = ttk.Entry(tab)
    phone_entry.grid(column=1, row=5)

    ttk.Button(tab, text="Add Professor", command=lambda: add_professor([
    professor_id_entry.get(),
    first_name_entry.get(),
    last_name_entry.get(),
    email_entry.get(),
    phone_entry.get(),
])).grid(column=0, row=6)
    

def setup_subjects_tab(tab):
    ttk.Label(tab, text="Subject Management").grid(column=0, row=0, padx=10, pady=10)
    ttk.Label(tab, text="Subject Name:").grid(column=0, row=1)
    subject_name_entry = ttk.Entry(tab)
    subject_name_entry.grid(column=1, row=1)
    # Add other subject details and CRUD operations:
    ttk.Label(tab, text="Professor ID:").grid(column=0, row=2)
    professor_id_entry = ttk.Entry(tab)
    professor_id_entry.grid(column=1, row=2)
    ttk.Button(tab, text="Add Subject", command=lambda: add_subject([subject_name_entry.get(), professor_id_entry.get()])).grid(column=0, row=3)

def setup_attendance_tab(tab):
    ttk.Label(tab, text="Attendance Management").grid(column=0, row=0, padx=10, pady=10)
    ttk.Label(tab, text="Student ID:").grid(column=0, row=1)
    student_id_entry = ttk.Entry(tab)
    student_id_entry.grid(column=1, row=1)
    # Marking and viewing attendance details:
    ttk.Label(tab, text="Subject ID:").grid(column=0, row=2)
    subject_id_entry = ttk.Entry(tab)
    subject_id_entry.grid(column=1, row=2)
    ttk.Label(tab, text="Date (YYYY-MM-DD):").grid(column=0, row=3)
    date_entry = ttk.Entry(tab)
    date_entry.grid(column=1, row=3)
    ttk.Label(tab, text="Status (Present/Absent):").grid(column=0, row=4)
    status_entry = ttk.Entry(tab)
    status_entry.grid(column=1, row=4)
    ttk.Button(tab, text="Record Attendance", command=lambda: record_attendance([student_id_entry.get(), subject_id_entry.get(), date_entry.get(), status_entry.get()])).grid(column=0, row=5)

def main():
    window = tk.Tk()
    window.title("Student and Admin Management System")

    user_type_var = tk.StringVar(value="student")
    tk.Radiobutton(window, text="Student Login", variable=user_type_var, value="student").pack()
    tk.Radiobutton(window, text="Admin Login", variable=user_type_var, value="admin").pack()

    username_entry = ttk.Entry(window)
    username_entry.pack()
    password_entry = ttk.Entry(window, show="*")
    password_entry.pack()

    def attempt_login():
        user_id = login_user(username_entry.get(), password_entry.get(), user_type_var.get())
        if user_id:
            if user_type_var.get() == "student":
                show_student_interface(user_id)
            else:
                show_admin_interface(user_id)

    ttk.Button(window, text="Login", command=attempt_login).pack()
    window.mainloop()

if __name__ == "__main__":
    main()
