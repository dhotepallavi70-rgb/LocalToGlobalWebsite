from flask import Flask, render_template, request, redirect, send_file
import sqlite3
from flask import Flask, render_template, request
import csv

app = Flask(__name__)

@app.route("/")
def home():

    ip = request.remote_addr

    browser = request.user_agent.string

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO visitors
        (ip_address,browser)
        VALUES (?,?)
        """,
        (ip,browser)
    )

    conn.commit()
    conn.close()

    return render_template("index.html")



# DATABASE SETUP
def init_db():
    cursor.execute("""
CREATE TABLE IF NOT EXISTS visitors(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT,
    browser TEXT,
    visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS students(

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

    conn.commit()
    conn.close()

init_db()

# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")

# SAVE STUDENT ENQUIRY
@app.route("/submit", methods=["POST"])
def submit():

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]

    qualification = request.form["qualification"]
    city = request.form["city"]

    country = request.form["country"]
    message = request.form["message"]

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO students
    (name,email,phone,qualification,city,country,message)

    VALUES(?,?,?,?,?,?,?)

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

    <p>
    Your consultation request has been submitted successfully.
    </p>

    <a href='/'>
    Back To Website
    </a>

    """

# ADMIN DASHBOARD
@app.route("/admin")
def admin():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    conn.close()

    html = """

    <html>

    <head>

    <title>Admin Dashboard</title>

    <style>

    body{
        font-family:Arial;
        padding:20px;
    }

    table{
        width:100%;
        border-collapse:collapse;
    }

    th,td{
        border:1px solid #ddd;
        padding:10px;
    }

    th{
        background:#003366;
        color:white;
    }

    a{
        text-decoration:none;
        padding:10px;
        background:green;
        color:white;
    }

    </style>

    </head>

    <body>

    <h1>Student Enquiries Dashboard</h1>

    <br>

    <form action='/search' method='GET'>

    <input
    type='text'
    name='q'
    placeholder='Search Student Name'>

    <button>
    Search
    </button>

    </form>

    <br>

    <a href='/export'>
    Export CSV
    </a>

    <br><br>

    <table>

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

    for s in students:

        html += f"""

        <tr>

        <td>{s[0]}</td>
        <td>{s[1]}</td>
        <td>{s[2]}</td>
        <td>{s[3]}</td>
        <td>{s[4]}</td>
        <td>{s[5]}</td>
        <td>{s[6]}</td>
        <td>{s[7]}</td>

        </tr>

        """

    html += """

    </table>

    </body>

    </html>

    """

    return html

# SEARCH STUDENT
@app.route("/search")
def search():

    keyword = request.args.get("q")

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE name LIKE ?",
        ('%' + keyword + '%',)
    )

    students = cursor.fetchall()

    conn.close()

    return str(students)

# EXPORT CSV
@app.route("/export")
def export_data():

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")

    rows = cursor.fetchall()

    conn.close()

    with open("students_export.csv","w",newline="") as file:

        writer = csv.writer(file)

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

    return send_file(
        "students_export.csv",
        as_attachment=True
    )

# RUN APP
if __name__ == "__main__":
    app.run(debug=True)