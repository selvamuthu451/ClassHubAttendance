from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    send_file
)
from datetime import datetime, timedelta, timezone
from database import get_connection
from openpyxl import Workbook
import random
import string
from datetime import datetime, timedelta, timezone

# ==========================================================
# 1. HELPER FUNCTION UPDATE
# ==========================================================
def get_current_class():
    ist_timezone = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist_timezone)
    
    weekday = now.weekday()
    current_minutes = now.hour * 60 + now.minute
    
    # ---------------------------------------------------------
    # SATURDAY MAPPING LOGIC (உங்கள் பழைய கோட்)
    # ---------------------------------------------------------
    if weekday == 5:
        today_date_str = now.strftime('%Y-%m-%d')
        saturday_schedule = {
            '2026-07-11': 0, '2026-07-25': 3, '2026-08-08': 4,
            '2026-08-22': 0, '2026-09-19': 3, '2026-10-10': 4,
            '2026-10-24': 3, '2026-10-31': 3, '2027-01-09': 4,
            '2027-01-23': 4, '2027-01-30': 4, '2027-02-13': 4,
            '2027-02-27': 4, '2027-03-13': 1, '2027-04-10': 2
        }
        if today_date_str in saturday_schedule:
            weekday = saturday_schedule[today_date_str]
        else:
            return None, None
            
    # ---------------------------------------------------------
    # TIMETABLE MATRIX WITH "SPLIT LABS"
    # ---------------------------------------------------------
    timetable = {
        0: { # Monday
            (8, 45, 10, 45): ("MONDAY_LAB", "1"),
            (11, 0, 12, 0): ("CSE105 - Computer Organization", "3"),
            (12, 0, 13, 0): ("MAT201R01 - Engineering Mathematics - III", "4"),
            (14, 0, 15, 0): ("ECE101R01 - Digital System Design", "6")
        },
        1: { # Tuesday
            (8, 45, 9, 45): ("MAT201R01 - Engineering Mathematics - III", "1"),
            (9, 45, 10, 45): ("ECE101R01 - Digital System Design", "2"),
            (11, 0, 12, 0): ("CSE208 - Java Programming", "3"),
            (12, 0, 13, 0): ("CSE103R01 - Data Structures", "4"),
            (14, 0, 15, 0): ("CSE105 - Computer Organization", "6")
        },
        2: { # Wednesday
            (9, 45, 10, 45): ("CSE103R01 - Data Structures", "2"),
            (11, 0, 12, 0): ("MAT201R01 - Engineering Mathematics - III", "3"),
            (12, 0, 13, 0): ("CSE105 - Computer Organization", "4"),
            (14, 0, 15, 0): ("ECE101R01 - Digital System Design", "6"),
            (15, 15, 16, 15): ("CSE208 - Java Programming", "7")
        },
        3: { # Thursday
            (8, 45, 9, 45): ("MAT201R01 - Engineering Mathematics - III", "1"),
            (9, 45, 10, 45): ("CSE105 - Computer Organization", "2"),
            (11, 0, 12, 0): ("CSE208 - Java Programming", "3"),
            (12, 0, 13, 0): ("ECE101R01 - Digital System Design", "4"),
            (14, 0, 15, 0): ("CSE103R01 - Data Structures", "6"),
            (15, 15, 17, 15): ("CSE208 JAVA LAB", "7")
        },
        4: { # Friday
            (14, 0, 15, 0): ("CSE103R01 - Data Structures", "6"),
            (15, 15, 17, 15): ("FRIDAY_LAB", "7")
        }
    }
    
    if weekday in timetable:
        for (start_h, start_m, end_h, end_m), (subject, period) in timetable[weekday].items():
            start_time = start_h * 60 + start_m
            end_time = end_h * 60 + end_m
            if start_time <= current_minutes <= end_time:
                return subject, period
                
    return None, None
app = Flask(__name__)

# ==========================================================
# LOGIN
# ==========================================================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT full_name
            FROM admin
            WHERE username=%s
            AND password=%s
        """, (username, password))

        admin = cursor.fetchone()

        if not admin:
            conn.close()
            return render_template(
                "login.html",
                error="Invalid Username or Password"
            )

        # -------------------------
        # Check Open Session
        # -------------------------
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
        dashboard = None
        recent_students = []

        if session:
            session_id = session[0]
            
            # Convert naive DB datetime to explicit UTC for the frontend
            end_time_naive = session[4]
            end_time_iso = end_time_naive.replace(tzinfo=timezone.utc).isoformat() if end_time_naive else None

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
                "total": total_students,
                "end_time_iso": end_time_iso
            }

        conn.close()

        return render_template(
            "dashboard.html",
            name=admin[0],
            dashboard=dashboard,
            recent_students=recent_students
        )

    return render_template("login.html")

# ==========================================================
# DASHBOARD
# ==========================================================
@app.route("/dashboard")
def dashboard():
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
    dashboard = None
    recent_students = []

    if session:
        session_id = session[0]
        
        # Convert naive DB datetime to explicit UTC for the frontend
        end_time_naive = session[4]
        end_time_iso = end_time_naive.replace(tzinfo=timezone.utc).isoformat() if end_time_naive else None

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
            "total": total_students,
            "end_time_iso": end_time_iso
        }

    conn.close()

    return render_template(
        "dashboard.html",
        name="Selvamuthu",
        dashboard=dashboard,
        recent_students=recent_students
    )

# ==========================================================
# 2. START ATTENDANCE ROUTE UPDATE
# ==========================================================
@app.route("/start", methods=["GET", "POST"])
def start_attendance():
    if request.method == "POST":
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT subject, period, attendance_code FROM attendance_sessions WHERE status='OPEN' LIMIT 1")
        active = cursor.fetchone()

        if active:
            conn.close()
            return render_template("start_attendance.html", error=f"Attendance is already OPEN.\nSubject: {active[0]} | Period: {active[1]} | Code: {active[2]}")

        subject = request.form["subject"]
        period = request.form["period"]
        duration = int(request.form["duration"])
        
        # பேட்ச் சேர்க்கும் லாஜிக்
        batch = request.form.get("batch", "All")
        if batch in ["Batch 1", "Batch 2"]:
            subject = f"{subject} ({batch})"

        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        now_utc = datetime.now(timezone.utc)
        end_time_utc = now_utc + timedelta(minutes=duration)
        
        now_str = now_utc.strftime('%Y-%m-%d %H:%M:%S')
        end_str = end_time_utc.strftime('%Y-%m-%d %H:%M:%S')
        date_str = now_utc.strftime('%Y-%m-%d')

        cursor.execute("""
            INSERT INTO attendance_sessions (subject, period, attendance_code, duration, session_date, start_time, end_time, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'OPEN')
        """, (subject, period, code, duration, date_str, now_str, end_str))

        conn.commit()
        conn.close()

        return render_template("attendance_started.html", subject=subject, period=period, duration=duration, code=code)

    auto_subject, auto_period = get_current_class()
    return render_template("start_attendance.html", auto_subject=auto_subject, auto_period=auto_period)

# ==========================================================
# 3. STUDENT ATTENDANCE ROUTE UPDATE (Validation Logic)
# ==========================================================
@app.route("/student", methods=["GET", "POST"])
def student():
    if request.method == "POST":
        register_number = request.form["register_number"].strip()
        attendance_code = request.form["attendance_code"].strip().upper()
        ip_address = request.remote_addr

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT student_name, nickname FROM students WHERE register_number=%s", (register_number,))
        student = cursor.fetchone()

        if not student:
            conn.close()
            return render_template("student.html", message="Invalid Register Number")

        student_name = student[0]
        nickname = student[1]
        display_name = nickname if nickname else student_name

        cursor.execute("SELECT session_id, subject FROM attendance_sessions WHERE attendance_code=%s AND status='OPEN'", (attendance_code,))
        session = cursor.fetchone()

        if not session:
            conn.close()
            return render_template("student.html", message="Invalid or Closed Attendance Code")

        session_id = session[0]
        session_subject = session[1]

        # -----------------------------------
        # முதல் 30 பேருக்கு மட்டும் அனுமதி வழங்கும் லாஜிக்
        # -----------------------------------
        if "(Batch 1)" in session_subject or "(Batch 2)" in session_subject:
            # ரெஜிஸ்டர் நம்பர் வரிசைப்படி (Ascending Order) டேட்டாபேஸிலிருந்து எடுக்கப்படும்
            cursor.execute("SELECT register_number FROM students ORDER BY register_number ASC")
            all_students = [str(row[0]).strip() for row in cursor.fetchall()]
            
            try:
                # வரிசையில் மாணவரின் எண் (0 முதல் 29 வரை இருந்தால் அவர் Batch 1)
                student_index = all_students.index(register_number)
                is_batch_1 = student_index < 30
                
                if "(Batch 1)" in session_subject and not is_batch_1:
                    conn.close()
                    return render_template("student.html", message="❌ Attendance Denied: This session is only for Batch 1 (First 30 students).")
                    
                if "(Batch 2)" in session_subject and is_batch_1:
                    conn.close()
                    return render_template("student.html", message="❌ Attendance Denied: This session is only for Batch 2 (Remaining students).")
            except ValueError:
                pass # Invalid Register Number (ஏற்கனவே மேலே சரிபார்க்கப்பட்டுவிட்டது)

        # -----------------------------------
        
        cursor.execute("SELECT 1 FROM attendance_records WHERE session_id=%s AND register_number=%s", (session_id, register_number))
        if cursor.fetchone():
            conn.close()
            return render_template("student.html", message="Attendance Already Submitted")

        cursor.execute("INSERT INTO attendance_records (session_id, register_number, submitted_time, ip_address) VALUES (%s, %s, NOW(), %s)", (session_id, register_number, ip_address))
        conn.commit()
        conn.close()

        return render_template("student.html", message=f"Attendance Submitted Successfully. Welcome {display_name}!")

    return render_template("student.html")
# ==========================================================
# DASHBOARD DATA API
# ==========================================================
@app.route("/dashboard_data")
def dashboard_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT session_id, subject, period, attendance_code, end_time
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
    
    # Send the absolute UTC end time string to the client instead of calculating 'remaining' seconds
    end_time_naive = session[4]
    end_time_iso = end_time_naive.replace(tzinfo=timezone.utc).isoformat() if end_time_naive else None

    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance_records WHERE session_id=%s", (session_id,))
    present = cursor.fetchone()[0]
    absent = total - present

    cursor.execute("""
        SELECT s.student_name, ar.submitted_time, ar.ip_address
        FROM attendance_records ar
        JOIN students s ON ar.register_number=s.register_number
        WHERE ar.session_id=%s
        ORDER BY ar.submitted_time DESC
        LIMIT 5
    """, (session_id,))
    recent = cursor.fetchall()

    cursor.execute("""
        SELECT ip_address, COUNT(*) AS total_students, GROUP_CONCAT(s.student_name SEPARATOR ', ')
        FROM attendance_records ar
        JOIN students s ON ar.register_number=s.register_number
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
        "end_time_iso": end_time_iso,
        "present": present,
        "absent": absent,
        "total": total,
        "recent": recent,
        "suspicious": suspicious
    })

# ==========================================================
# CLOSE ATTENDANCE
# ==========================================================
@app.route("/close_attendance")
def close_attendance():
    print("========== CLOSE ATTENDANCE CALLED ==========")
    import traceback
    traceback.print_stack()

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

# ==========================================================
# SESSION HISTORY & DETAILS & DOWNLOADS
# (These remain completely untouched and work as expected)
# ==========================================================
@app.route("/history")
def history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT session_id, session_date, subject, period, start_time, end_time, status
        FROM attendance_sessions
        ORDER BY session_id DESC
    """)
    sessions = cursor.fetchall()
    conn.close()
    return render_template("session_history.html", sessions=sessions)

@app.route("/session/<int:session_id>")
def session_details(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT subject, period, session_date, start_time, end_time, status FROM attendance_sessions WHERE session_id=%s", (session_id,))
    session = cursor.fetchone()
    if not session:
        conn.close()
        return "Session not found."
    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM attendance_records WHERE session_id=%s", (session_id,))
    present = cursor.fetchone()[0]
    absent = total - present
    cursor.execute("""
        SELECT s.register_number, s.student_name, ar.submitted_time, ar.ip_address
        FROM attendance_records ar
        JOIN students s ON ar.register_number=s.register_number
        WHERE ar.session_id=%s
        ORDER BY s.register_number
    """, (session_id,))
    present_students = cursor.fetchall()
    cursor.execute("""
        SELECT register_number, student_name
        FROM students
        WHERE register_number NOT IN (SELECT register_number FROM attendance_records WHERE session_id=%s)
        ORDER BY register_number
    """, (session_id,))
    absent_students = cursor.fetchall()
    cursor.execute("""
        SELECT ip_address, COUNT(*) AS total_students, GROUP_CONCAT(s.student_name SEPARATOR ', ')
        FROM attendance_records ar
        JOIN students s ON ar.register_number=s.register_number
        WHERE ar.session_id=%s
        GROUP BY ip_address
        HAVING COUNT(*) > 1
    """, (session_id,))
    suspicious_ips = cursor.fetchall()
    conn.close()
    return render_template("session_details.html", session=session, total=total, present=present, absent=absent, present_students=present_students, absent_students=absent_students, suspicious_ips=suspicious_ips, session_id=session_id)

@app.route("/download_absentees")
def download_absentees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT session_id FROM attendance_sessions ORDER BY session_id DESC LIMIT 1")
    session = cursor.fetchone()
    conn.close()
    if not session:
        return "No attendance session found."
    return redirect(url_for("download_excel", session_id=session[0]))

# ==========================================================
# DOWNLOAD EXCEL REPORT
# ==========================================================

@app.route("/download/<int:session_id>")
def download_excel(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    wb = Workbook()

    ws = wb.active
    ws.title = "Attendance Report"

    # ------------------------------------------
    # Session Information
    # ------------------------------------------

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
    """, (session_id,))

    session = cursor.fetchone()

    if not session:
        conn.close()
        return "Session not found."

    ws.append(["CLASSHUB ATTENDANCE REPORT"])
    ws.append([])

    ws.append(["Subject", session[0]])
    ws.append(["Period", session[1]])
    ws.append(["Date", str(session[2])])
    ws.append(["Start Time", str(session[3])])
    ws.append(["End Time", str(session[4])])
    ws.append(["Status", session[5]])

    ws.append([])

    # ------------------------------------------
    # Summary
    # ------------------------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM students"
    )

    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance_records
        WHERE session_id=%s
    """, (session_id,))

    present = cursor.fetchone()[0]

    absent = total - present

    ws.append(["SUMMARY"])
    ws.append(["Total Students", total])
    ws.append(["Present", present])
    ws.append(["Absent", absent])

    ws.append([])
    ws.append([])

    # ------------------------------------------
    # Absent Students
    # ------------------------------------------

    ws.append(["ABSENT STUDENTS"])
    ws.append(["Register Number", "Student Name"])

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

    # ------------------------------------------
    # Security Monitor
    # ------------------------------------------

    ws.append([])
    ws.append(["SECURITY MONITOR"])
    ws.append(["IP Address", "Students", "Total"])

    cursor.execute("""
        SELECT
            ip_address,
            GROUP_CONCAT(
                s.student_name
                SEPARATOR ', '
            ),
            COUNT(*)
        FROM attendance_records ar
        JOIN students s
            ON ar.register_number=s.register_number
        WHERE ar.session_id=%s
        GROUP BY ip_address
        HAVING COUNT(*) > 1
    """, (session_id,))

    suspicious = cursor.fetchall()

    if suspicious:
        for row in suspicious:
            ws.append(row)
    else:
        ws.append([
            "No suspicious activity detected",
            "",
            ""
        ])

    # ------------------------------------------
    # Auto Column Width
    # ------------------------------------------

    for column in ws.columns:

        length = 0
        column_letter = column[0].column_letter

        for cell in column:
            try:
                if len(str(cell.value)) > length:
                    length = len(str(cell.value))
            except:
                pass

        ws.column_dimensions[column_letter].width = length + 5

    # ------------------------------------------
    # Dynamic Filename Generation
    # ------------------------------------------
    
    raw_subject = session[0]
    session_date = str(session[2])
    
    # Extract just the course code (e.g., 'CSE105' from 'CSE105 - Computer Organization')
    # Replace slashes and spaces to ensure it is a valid filename for Windows/Mac
    course_code = raw_subject.split(' - ')[0].replace('/', '_').replace(' ', '')
    
    # Generate format: Attendance_report_(CSE105_2026-07-28).xlsx
    filename = f"Attendance_report_({course_code}_{session_date}).xlsx"

    wb.save(filename)

    conn.close()

    return send_file(
        filename,
        as_attachment=True
    )

@app.route("/fix-db")
def fix_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Increase the character limit to 150 to fit the new long course names
        cursor.execute("ALTER TABLE attendance_sessions MODIFY subject VARCHAR(150);")
        conn.commit()
        conn.close()
        return "✅ Database updated successfully! You can now use long subject names. Go back to the dashboard and try again."
    except Exception as e:
        return f"❌ An error occurred: {e}"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
