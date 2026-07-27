from flask import Flask, render_template, request, jsonify, redirect, url_for,send_file
from database import get_connection
from openpyxl import Workbook
import random
import string

app = Flask(__name__)

# -------------------- LOGIN --------------------

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        sql = """
        SELECT full_name
        FROM admin
        WHERE username=%s AND password=%s
        """

        cursor.execute(sql, (username, password))

        admin = cursor.fetchone()

        if admin:

            # Get latest OPEN attendance session
            cursor.execute("""
                SELECT session_id, subject, period, attendance_code
                FROM attendance_sessions
                WHERE status='open'
                ORDER BY session_id DESC
                LIMIT 1
            """)

            session = cursor.fetchone()
            print("Session:", session)

            dashboard = None
            recent_students = []

            if session:

                session_id = session[0]

                # Total students
                cursor.execute("SELECT COUNT(*) FROM students")
                total_students = cursor.fetchone()[0]

                # Present students
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM attendance_records
                    WHERE session_id=%s
                """, (session_id,))
                present = cursor.fetchone()[0]

                absent = total_students - present

                # Recent attendance (last 5 students)
                cursor.execute("""
                    SELECT
                        s.student_name,
                        ar.submitted_time,
                        ar.ip_address
                    FROM attendance_records ar
                    JOIN students s
                        ON ar.register_number = s.register_number
                    WHERE ar.session_id=%s
                    ORDER BY ar.submitted_time DESC
                    LIMIT 5
                """, (session_id,))

                recent_students = cursor.fetchall()

                dashboard = {
                    "status": "OPEN",
                    "subject": session[1],
                    "period": session[2],
                    "code": session[3],
                    "present": present,
                    "absent": absent,
                    "total": total_students
                }
            conn.close()
            return render_template(
                "dashboard.html",
                name=admin[0],
                dashboard=dashboard,
                recent_students=recent_students
            )

        else:
            conn.close()
            return render_template(
                "login.html",
                error="Invalid Username or Password"
            )

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    conn = get_connection()
    cursor = conn.cursor()

    # Get latest OPEN attendance session
    cursor.execute("""
        SELECT
            session_id,
            subject,
            period,
            attendance_code
        FROM attendance_sessions
        WHERE status='OPEN'
        ORDER BY session_id DESC
        LIMIT 1
    """)

    session = cursor.fetchone()

    dashboard = None
    recent_students = []

    if session:

        session_id = session[0]

        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM attendance_records
            WHERE session_id=%s
        """, (session_id,))

        present = cursor.fetchone()[0]
        absent = total_students - present

        cursor.execute("""
            SELECT
                s.student_name,
                ar.submitted_time,
                ar.ip_address
            FROM attendance_records ar
            JOIN students s
            ON ar.register_number=s.register_number
            WHERE ar.session_id=%s
            ORDER BY ar.submitted_time DESC
            LIMIT 5
        """, (session_id,))

        recent_students = cursor.fetchall()

        dashboard = {
            "status": "OPEN",
            "subject": session[1],
            "period": session[2],
            "code": session[3],
            "present": present,
            "absent": absent,
            "total": total_students
        }

    conn.close()

    return render_template(
        "dashboard.html",
        name="Selvamuthu",
        dashboard=dashboard,
        recent_students=recent_students
    )

# -------------------- START ATTENDANCE --------------------

@app.route("/start", methods=["GET", "POST"])
def start_attendance():

    if request.method == "POST":
        # Check if an attendance session is already OPEN
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT subject, period, attendance_code
        FROM attendance_sessions
        WHERE status='OPEN'
        LIMIT 1
        """)

        active = cursor.fetchone()

        if active:
            conn.close()

            return render_template(
                "start_attendance.html",
                error=f"Attendance is already OPEN.\nSubject: {active[0]} | Period: {active[1]} | Code: {active[2]}"
            )

        subject = request.form["subject"]
        period = request.form["period"]
        duration = int(request.form["duration"])

        code = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=8
            )
        )

        sql = """
        INSERT INTO attendance_sessions
        (
        subject,
        period,
        attendance_code,
        duration,
        session_date,
        start_time,
        end_time,
        status
        )

        VALUES
        (
        %s,
        %s,
        %s,
        %s,
        CURDATE(),
        NOW(),
        DATE_ADD(NOW(), INTERVAL %s MINUTE),
        'OPEN'
        )
        """

        cursor.execute(sql,
                       (subject,
                        period,
                        code,
                        duration,
                        duration))

        conn.commit()
        conn.close()

        return render_template(
            "attendance_started.html",
            subject=subject,
            period=period,
            duration=duration,
            code=code
        )

    return render_template("start_attendance.html")

@app.route("/student", methods=["GET", "POST"])
def student():

    if request.method == "POST":

        register_number = request.form["register_number"]
        attendance_code = request.form["attendance_code"]
        ip_address = request.remote_addr

        conn = get_connection()
        cursor = conn.cursor()

        # Check student exists
        cursor.execute(
            "SELECT student_name,nickname FROM students WHERE register_number=%s",
            (register_number,)
        )

        student = cursor.fetchone()

        if student:
            real_name = student[0]
            nickname = student[1]

            if nickname:
                display_name = nickname
            else:
                display_name = real_name

        if not student:
            conn.close()
            return render_template(
                "student.html",
                message="Invalid Register Number"
            )

        # Check attendance session
        cursor.execute("""
        SELECT session_id
        FROM attendance_sessions
        WHERE attendance_code=%s
        AND status='OPEN'
        """, (attendance_code,))

        session = cursor.fetchone()

        if not session:
            conn.close()
            return render_template(
                "student.html",
                message="Invalid or Closed Attendance Code"
            )

        session_id = session[0]

        # Check duplicate attendance
        cursor.execute("""
        SELECT *
        FROM attendance_records
        WHERE session_id=%s
        AND register_number=%s
        """, (session_id, register_number))

        if cursor.fetchone():
            conn.close()
            return render_template(
                "student.html",
                message="Attendance Already Submitted"
            )

        # Save attendance
        cursor.execute("""
        INSERT INTO attendance_records
        (session_id, register_number, submitted_time, ip_address)
        VALUES(%s,%s,NOW(),%s)
        """, (session_id, register_number, ip_address))

        conn.commit()

        conn.close()

        return render_template(
            "student.html",
            message=f"Attendance Submitted Successfully. Welcome {display_name}"
        )

    return render_template("student.html")

# -------------------- DASHBOARD DATA API --------------------

@app.route("/dashboard_data")
def dashboard_data():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
    session_id,
    subject,
    period,
    attendance_code,
    end_time
    FROM attendance_sessions
    WHERE status='OPEN'
    ORDER BY session_id DESC
    LIMIT 1
    """)

    session = cursor.fetchone()

    if not session:
        conn.close()
        return jsonify({"active": False})

    session_id = session[0]

    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance_records
        WHERE session_id=%s
    """, (session_id,))
    present = cursor.fetchone()[0]

    absent = total - present

    cursor.execute("""
    SELECT
        s.student_name,
        ar.submitted_time,
        ar.ip_address
    FROM attendance_records ar
    JOIN students s
        ON ar.register_number=s.register_number
    WHERE ar.session_id=%s
    ORDER BY ar.submitted_time DESC
    LIMIT 5
""", (session_id,))

    recent = cursor.fetchall()
    # Security Monitor
    cursor.execute("""
    SELECT
        ip_address,
        COUNT(*) AS total_students,
        GROUP_CONCAT(s.student_name SEPARATOR ', ')
    FROM attendance_records ar
    JOIN students s
        ON ar.register_number = s.register_number
    WHERE ar.session_id=%s
    GROUP BY ip_address
    HAVING COUNT(*) > 1
    """, (session_id,))

    suspicious = cursor.fetchall()

    conn.close()

    return jsonify({
        "active": True,
        "subject": session[1],
        "period": session[2],
        "code": session[3],
        "end_time": session[4].strftime("%Y-%m-%d %H:%M:%S"),
        "present": present,
        "absent": absent,
        "total": total,
        "recent": recent,
        "suspicious": suspicious
    })

@app.route("/close_attendance")
def close_attendance():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE attendance_sessions
        SET status='CLOSED'
        WHERE status='OPEN'
    """)

    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route("/history")
def history():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        session_id,
        session_date,
        subject,
        period,
        start_time,
        end_time,
        status
    FROM attendance_sessions
    ORDER BY session_id DESC
    """)

    sessions = cursor.fetchall()

    conn.close()

    return render_template(
        "session_history.html",
        sessions=sessions
    )

@app.route("/session/<int:session_id>")
def session_details(session_id):

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""

    SELECT

        subject,

        period,

        session_date,

        start_time,

        end_time,

        status

    FROM attendance_sessions

    WHERE session_id=%s

    """,(session_id,))

    session=cursor.fetchone()
    cursor.execute(

        "SELECT COUNT(*) FROM students"

    )

    total=cursor.fetchone()[0]
    cursor.execute("""

    SELECT COUNT(*)

    FROM attendance_records

    WHERE session_id=%s

    """,(session_id,))

    present=cursor.fetchone()[0]
    absent=total-present
    cursor.execute("""

    SELECT

        s.register_number,

        s.student_name,

        ar.submitted_time,

        ar.ip_address

    FROM attendance_records ar

    JOIN students s

        ON ar.register_number=s.register_number

    WHERE ar.session_id=%s

    ORDER BY s.register_number

    """,(session_id,))

    present_students=cursor.fetchall()
    cursor.execute("""

    SELECT

        register_number,

        student_name

    FROM students

    WHERE register_number NOT IN

    (

        SELECT register_number

        FROM attendance_records

        WHERE session_id=%s

    )

    ORDER BY register_number

    """,(session_id,))

    absent_students=cursor.fetchall()
    # Suspicious Activity (Same IP Address)

    cursor.execute("""
    SELECT
        ip_address,
        COUNT(*) AS total_students,
        GROUP_CONCAT(s.student_name SEPARATOR ', ')
    FROM attendance_records ar
    JOIN students s
        ON ar.register_number = s.register_number
    WHERE session_id=%s
    GROUP BY ip_address
    HAVING COUNT(*) > 1
    """, (session_id,))

    suspicious_ips = cursor.fetchall()
    conn.close()

    return render_template(
    "session_details.html",
    session=session,
    total=total,
    present=present,
    absent=absent,
    present_students=present_students,
    absent_students=absent_students,
    suspicious_ips=suspicious_ips,
    session_id=session_id
)

@app.route("/download_absentees")
def download_absentees():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT session_id
        FROM attendance_sessions
        ORDER BY session_id DESC
        LIMIT 1
    """)

    session = cursor.fetchone()

    conn.close()

    if not session:
        return "No active attendance session."

    return redirect(url_for("download_excel", session_id=session[0]))

@app.route("/download/<int:session_id>")
def download_excel(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance Report"

    # -----------------------------
    # Session Information
    # -----------------------------

    cursor.execute("""
    SELECT
        subject,
        period,
        session_date
    FROM attendance_sessions
    WHERE session_id=%s
    """, (session_id,))

    session = cursor.fetchone()

    ws.append(["Attendance Report"])
    ws.append([])

    ws.append(["Subject", session[0]])
    ws.append(["Period", session[1]])
    ws.append(["Date", str(session[2])])

    ws.append([])

    # -----------------------------
    # Summary
    # -----------------------------

    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM attendance_records
    WHERE session_id=%s
    """, (session_id,))

    present = cursor.fetchone()[0]
    absent = total - present

    ws.append(["Summary"])
    ws.append(["Total Students", total])
    ws.append(["Present", present])
    ws.append(["Absent", absent])

    ws.append([])
    # -----------------------------
    # Absent Students
    # -----------------------------

    ws.append(["Absent Students"])

    ws.append([
        "Register Number",
        "Student Name"
    ])

    cursor.execute("""
    SELECT
        register_number,
        student_name
    FROM students
    WHERE register_number NOT IN
    (
        SELECT register_number
        FROM attendance_records
        WHERE session_id=%s
    )
    ORDER BY register_number
    """, (session_id,))

    for row in cursor.fetchall():
        ws.append(row)

    ws.append([])
    ws.append([])

    # -----------------------------
    # Suspicious Activity
    # -----------------------------

    ws.append(["Security Monitor"])

    ws.append([
        "IP Address",
        "Students",
        "Total"
    ])

    cursor.execute("""
    SELECT
        ip_address,
        GROUP_CONCAT(s.student_name SEPARATOR ', '),
        COUNT(*)
    FROM attendance_records ar
    JOIN students s
        ON ar.register_number=s.register_number
    WHERE session_id=%s
    GROUP BY ip_address
    HAVING COUNT(*)>1
    """, (session_id,))

    suspicious = cursor.fetchall()

    if suspicious:
        for row in suspicious:
            ws.append(row)
    else:
        ws.append(["No suspicious activity detected"])

    filename = f"Attendance_Report_{session_id}.xlsx"

    wb.save(filename)

    conn.close()

    return send_file(
        filename,
        as_attachment=True
    )

#--------------------------------RUN---------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
