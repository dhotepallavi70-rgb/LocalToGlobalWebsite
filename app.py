from flask import Flask, render_template, request, redirect
import sqlite3
import csv
from io import StringIO
from flask import Response
from flask import session

app = Flask(__name__)
app.secret_key = "LocalToGlobal2026"

# ---------------------------
# DATABASE INITIALIZATION
# ---------------------------

def init_db():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    # Student enquiries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        qualification TEXT,
        city TEXT,
        country TEXT,
        message TEXT
    )
    """)

    # Visitor tracking table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS visitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT,
        browser TEXT,
        visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


init_db()

# ---------------------------
# HOME PAGE
# ---------------------------

@app.route("/")
def home():

    ip = request.remote_addr
    browser = request.user_agent.string

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO visitors (ip_address, browser)
    VALUES (?, ?)
    """, (ip, browser))

    conn.commit()
    conn.close()

    return render_template("index.html")


# ---------------------------
# FORM SUBMISSION
# ---------------------------

@app.route("/submit", methods=["POST"])
def submit():

    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    qualification = request.form.get("qualification")
    city = request.form.get("city")
    country = request.form.get("country")
    message = request.form.get("message")

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO students
    (name,email,phone,qualification,city,country,message)
    VALUES (?,?,?,?,?,?,?)
    """,
    (
        name,
        email,
        phone,
        qualification,
        city,
        country,
        message
    ))

    conn.commit()
    conn.close()

    return """
    <h2>Thank You!</h2>
    <p>Your consultation request has been submitted successfully.</p>
    <a href="/">Go Back Home</a>
    """


# ---------------------------
# ADMIN DASHBOARD
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "LocalToGlobal@123":
            session["admin"] = True
            return redirect("/admin")

        return """
        <h2>Invalid Login</h2>
        <a href='/login'>Try Again</a>
        """

    return """
    <h2>Admin Login</h2>

    <form method='POST'>
        <input type='text' name='username' placeholder='Username'>
        <br><br>

        <input type='password' name='password' placeholder='Password'>
        <br><br>

        <button type='submit'>Login</button>
    </form>
    """
@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students ORDER BY id DESC")
    students = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM students")
    student_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM visitors")
    visitor_count = cursor.fetchone()[0]

    conn.close()

    html = f"""
    <html>
    <head>
        <title>Admin Dashboard</title>
    </head>
    <body>

    <h1>Local To Global - Admin Dashboard</h1>

    <h3>Total Student Enquiries: {student_count}</h3>
    <h3>Total Website Visitors: {visitor_count}</h3>

    <br>

    <a href="/export">
        Export Student Data
    </a>

    <br><br>

    <table border="1" cellpadding="10">

        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Qualification</th>
            <th>City</th>
            <th>Country</th>
            <th>Message</th>
        </tr>
    """

    for student in students:

        html += f"""
        <tr>
            <td>{student[0]}</td>
            <td>{student[1]}</td>
            <td>{student[2]}</td>
            <td>{student[3]}</td>
            <td>{student[4]}</td>
            <td>{student[5]}</td>
            <td>{student[6]}</td>
            <td>{student[7]}</td>
        </tr>
        """

    html += """
    </table>

    </body>
    </html>
    """

    return html


# ---------------------------
# EXPORT CSV
# ---------------------------

@app.route("/export")
def export():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()

    conn.close()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Name",
        "Email",
        "Phone",
        "Qualification",
        "City",
        "Country",
        "Message"
    ])

    writer.writerows(rows)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=students.csv"
        }
    )


# ---------------------------
# RUN APP
# ---------------------------

if __name__ == "__main__":
    app.run(debug=True)
