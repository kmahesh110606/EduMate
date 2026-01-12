import os
import random
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, flash, get_flashed_messages, send_from_directory, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, apology
from datetime import datetime
import openpyxl
import json



app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("postgresql://postgres:5253@localhost:5432/lms_db")


@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.errorhandler(404)
def not_found(e):
    return render_template("notfound.html"), 404


@app.route("/login", methods=["GET", "POST"])
def login(error=None, msg=None, warning=None):
    if request.method == "POST":
        email = request.form.get("email")
        reg_no = request.form.get("reg_no")
        password = request.form.get("password")

        user = []

        if email:
            user = db.execute("SELECT * FROM users WHERE email = %s", email)
        elif reg_no:
            user = db.execute("SELECT * FROM users WHERE reg_no = %s", reg_no)
        else:
            return render_template("login.html", msg=None, error="Please enter Email or Registration Number.", warning=None)

        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            return render_template("login.html", msg=None, error="Invalid credentials. Please try again.", warning=None)

        session["user_id"] = user[0]["id"]
        session["role"] = user[0]["role"]

        if session["role"] == "student":
            return redirect("/dashboard")
        elif session["role"] == "faculty":
            return redirect("/dashboard")

    return render_template("login.html", error=error, msg=msg, warning=warning)


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect("/login")



@app.route("/register", methods=["GET", "POST"])
def register(msg=None, error=None, warning=None):
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        reg_no = request.form.get("reg_no")
        contact = request.form.get("contact")
        role = request.form.get("role")

        if not name or not email or not password or not role:
            return render_template("register.html", warning="All fields are required")

        existing_user = db.execute("SELECT * FROM users WHERE email = %s", email)
        if len(existing_user) > 0:
            return render_template("register.html", error="Email already registered")

        hash_pw = generate_password_hash(password)
        db.execute("INSERT INTO users (name, email, hash, role, reg_no, contact) VALUES (%s, %s, %s, %s, %s, %s)", name, email, hash_pw, role, reg_no, contact)


        return login(msg="Registered successfully! Please log in to continue.")

    return render_template("register.html", msg=msg, error=error, warning=warning)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    # Fetch current user details
    user = db.execute("SELECT * FROM users WHERE id = %s", session["user_id"])[0]

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        reg_no = request.form.get("reg_no")
        contact = request.form.get("contact")
        password = request.form.get("password")

        # Update fields
        if password:
            hash_pw = generate_password_hash(password)
            db.execute("UPDATE users SET name=%s, email=%s, reg_no=%s, contact=%s, hash=%s WHERE id=%s",
                       name, email, reg_no, contact, hash_pw, session["user_id"])
        else:
            db.execute("UPDATE users SET name=%s, email=%s, reg_no=%s, contact=%s WHERE id=%s",
                       name, email, reg_no, contact, session["user_id"])

        return render_template("profile.html", user=user, msg="Profile updated successfully!")

    return render_template("profile.html", user=user)


@app.route("/deleteuser", methods=["POST"])
@login_required
def delete_user():
    user_rows = db.execute("SELECT * FROM users WHERE id = %s", session["user_id"])
    if not user_rows:
        session.clear()
        flash("User not found.", "error")
        return redirect("/login")

    user = user_rows[0]
    password = request.form.get("password") or ""
    confirm_text = (request.form.get("confirm_text") or "").strip().lower()
    expected = f"delete {user.get('name', '')}".strip().lower()

    if confirm_text != expected:
        return render_template(
            "profile.html",
            user=user,
            error=f"Confirmation text must match: '{expected}'",
        )

    if not password or not check_password_hash(user["hash"], password):
        return render_template(
            "profile.html",
            user=user,
            error="Incorrect password.",
        )

    user_id = session["user_id"]

    # Delete dependent records first to avoid FK issues
    if user.get("role") == "faculty":
        # Delete quiz attempts for quizzes belonging to faculty's classes
        db.execute(
            "DELETE FROM quiz_attempts WHERE quiz_id IN (SELECT q.quiz_id FROM quizzes q JOIN classrooms c ON q.class_no = c.class_no WHERE c.faculty_id = %s)",
            user_id,
        )
        # Delete quizzes for faculty's classes
        db.execute(
            "DELETE FROM quizzes WHERE class_no IN (SELECT class_no FROM classrooms WHERE faculty_id = %s)",
            user_id,
        )
        # Remove enrollments for faculty's classes
        db.execute(
            "DELETE FROM enrollments WHERE class_no IN (SELECT class_no FROM classrooms WHERE faculty_id = %s)",
            user_id,
        )
        # Delete classrooms
        db.execute("DELETE FROM classrooms WHERE faculty_id = %s", user_id)
        # If courses are faculty-owned, remove them too (prevents FK blocks)
        db.execute("DELETE FROM courses WHERE faculty_id = %s", user_id)
    else:
        # Student: remove attempts and enrollments
        db.execute("DELETE FROM quiz_attempts WHERE student_id = %s", user_id)
        db.execute("DELETE FROM enrollments WHERE student_id = %s", user_id)

    db.execute("DELETE FROM users WHERE id = %s", user_id)
    session.clear()
    flash("Account deleted successfully.", "success")
    return redirect("/login")


@app.route("/deleteclass", methods=["POST"])
@login_required
def delete_class():
    if session.get("role") != "faculty":
        return dashboard(error="Only faculty can delete classes.")

    class_no = request.form.get("class_no")
    if not class_no:
        return dashboard(error="Missing class number.")

    classroom_rows = db.execute("SELECT * FROM classrooms WHERE class_no = %s", class_no)
    if not classroom_rows:
        return dashboard(error="Class not found.")
    if classroom_rows[0].get("faculty_id") != session["user_id"]:
        return dashboard(error="You do not have access to delete this class.")

    # Delete attempts -> quizzes -> enrollments -> classroom
    db.execute("DELETE FROM quiz_attempts WHERE quiz_id IN (SELECT quiz_id FROM quizzes WHERE class_no = %s)", class_no)
    db.execute("DELETE FROM quizzes WHERE class_no = %s", class_no)
    db.execute("DELETE FROM enrollments WHERE class_no = %s", class_no)
    db.execute("DELETE FROM classrooms WHERE class_no = %s", class_no)

    return dashboard(msg=f"Class {class_no} deleted successfully.")


@app.route("/deletequiz", methods=["POST"])
@login_required
def delete_quiz():
    if session.get("role") != "faculty":
        return dashboard(error="Only faculty can delete quizzes.")

    quiz_id = request.form.get("quiz_id")
    if not quiz_id:
        return dashboard(error="Missing quiz id.")

    quiz_rows = db.execute(
        "SELECT q.* FROM quizzes q JOIN classrooms c ON q.class_no = c.class_no WHERE q.quiz_id = %s AND c.faculty_id = %s",
        quiz_id,
        session["user_id"],
    )
    if not quiz_rows:
        return dashboard(error="Quiz not found or access denied.")

    db.execute("DELETE FROM quiz_attempts WHERE quiz_id = %s", quiz_id)
    db.execute("DELETE FROM quizzes WHERE quiz_id = %s", quiz_id)
    return dashboard(msg="Quiz deleted successfully.")


@app.route("/dashboard")
@login_required
def dashboard(error=None, msg=None, warning=None):

    if session["role"] == "student":
        details = db.execute("SELECT * FROM users WHERE id = %s", session["user_id"])[0]
        courses = db.execute("SELECT * FROM enrollments WHERE student_id = %s", session["user_id"])
        quizzes = db.execute(
            "SELECT * FROM quizzes WHERE status != 'archive' AND class_no IN (SELECT class_no FROM enrollments WHERE student_id = %s) "
            "ORDER BY CASE WHEN status IN ('live','active') THEN 0 WHEN status IN ('stopped','draft') THEN 1 ELSE 2 END, quiz_id DESC",
            session["user_id"],
        )
        classes = db.execute("SELECT c.*, u.name AS faculty_name FROM classrooms c JOIN enrollments e ON c.class_no = e.class_no JOIN users u ON c.faculty_id = u.id WHERE e.student_id = %s", session['user_id']) or None
        return render_template("dashboard.html", details=details, courses=courses, quizzes=quizzes, error=error, msg=msg, warning=warning, classes=classes)

    elif session["role"] == "faculty":
        details = db.execute("SELECT * FROM users WHERE id = %s", session["user_id"])[0]
        courses = db.execute("SELECT * FROM courses WHERE faculty_id = %s", session["user_id"])
        classes = db.execute("SELECT * FROM classrooms WHERE faculty_id = %s", session["user_id"])
        quizzes = db.execute(
            "SELECT * FROM quizzes WHERE status != 'archive' AND class_no IN (SELECT class_no FROM classrooms WHERE faculty_id = %s) "
            "ORDER BY CASE WHEN status IN ('live','active') THEN 0 WHEN status IN ('stopped','draft') THEN 1 ELSE 2 END, quiz_id DESC",
            session["user_id"],
        )
        return render_template("dashboard.html", details=details, courses=courses, classes=classes, quizzes=quizzes, error=error, msg=msg, warning=warning)
    


@app.route("/join", methods=["POST"])
@login_required
def join_class():
    if session["role"] != "student":
        flash("Only students can join classes.", "error")
        return redirect("/dashboard")

    class_no = request.form.get("class_no")

    # Check if class exists
    existing_class = db.execute("SELECT * FROM classrooms WHERE class_no = %s", class_no)
    if len(existing_class) == 0:
        return dashboard(error="Class not found.")

    # Check if already enrolled
    existing_enrollment = db.execute(
        "SELECT * FROM enrollments WHERE student_id = %s AND class_no = %s",
        session["user_id"], class_no
    )
    if len(existing_enrollment) > 0:
        return dashboard(warning="Already enrolled in this class.")

    # Safe to insert
    db.execute(
        "INSERT INTO enrollments (student_id, class_no) VALUES (%s, %s)",
        session["user_id"], class_no
    )
    return dashboard(msg="Successfully joined the class.")


@app.route("/leaveclass", methods=["POST"])
@login_required
def leave_class():
    if session.get("role") != "student":
        flash("Only students can leave classes.", "error")
        return redirect("/dashboard")

    class_no = request.form.get("class_no")
    if not class_no:
        flash("Missing class number.", "error")
        return redirect("/dashboard")

    enrollment_rows = db.execute(
        "SELECT * FROM enrollments WHERE student_id = %s AND class_no = %s",
        session["user_id"],
        class_no,
    )
    if not enrollment_rows:
        flash("You are not enrolled in this class.", "warning")
        return redirect("/dashboard")

    # Remove attempts for quizzes in this class (optional but keeps data consistent)
    db.execute(
        "DELETE FROM quiz_attempts WHERE student_id = %s AND quiz_id IN (SELECT quiz_id FROM quizzes WHERE class_no = %s)",
        session["user_id"],
        class_no,
    )
    db.execute(
        "DELETE FROM enrollments WHERE student_id = %s AND class_no = %s",
        session["user_id"],
        class_no,
    )

    flash(f"Left class {class_no}.", "success")
    return redirect("/dashboard")


@app.route("/removestudent", methods=["POST"])
@login_required
def remove_student_from_class():
    if session.get("role") != "faculty":
        flash("Only faculty can remove students.", "error")
        return redirect("/dashboard")

    class_no = request.form.get("class_no")
    student_id = request.form.get("student_id")
    if not class_no or not student_id:
        flash("Missing class or student.", "error")
        return redirect("/dashboard")

    classroom_rows = db.execute("SELECT * FROM classrooms WHERE class_no = %s", class_no)
    if not classroom_rows:
        flash("Class not found.", "error")
        return redirect("/dashboard")
    if classroom_rows[0].get("faculty_id") != session["user_id"]:
        flash("Access denied.", "error")
        return redirect("/dashboard")

    # Ensure student is enrolled
    enrollment_rows = db.execute(
        "SELECT * FROM enrollments WHERE student_id = %s AND class_no = %s",
        student_id,
        class_no,
    )
    if not enrollment_rows:
        flash("Student is not enrolled in this class.", "warning")
        return redirect(f"/class/{class_no}")

    # Remove student's attempts for quizzes in this class, then unenroll
    db.execute(
        "DELETE FROM quiz_attempts WHERE student_id = %s AND quiz_id IN (SELECT quiz_id FROM quizzes WHERE class_no = %s)",
        student_id,
        class_no,
    )
    db.execute(
        "DELETE FROM enrollments WHERE student_id = %s AND class_no = %s",
        student_id,
        class_no,
    )

    flash("Student removed from class.", "success")
    return redirect(f"/class/{class_no}")


@app.route("/create_class", methods=["GET", "POST"])
@login_required
def create_class():
    if session["role"] != "faculty":
        flash("Only faculty can create classes.", "error")
        return redirect("/dashboard")

    if request.method == "GET":
        return render_template("create_class.html")

    nickname = request.form.get("nickname")
    class_no = request.form.get("class_no")
    course_code = request.form.get("course_code")

    existing_class = db.execute("SELECT * FROM classrooms WHERE class_no = %s", class_no)
    if len(existing_class) > 0:
        flash("Class number already exists.", "error")
        return redirect("/dashboard")

    db.execute("INSERT INTO classrooms (nickname, class_no, course_code, faculty_id) VALUES (%s, %s, %s, %s)", nickname, class_no, course_code, session["user_id"])
    return dashboard(msg="Class created successfully.")




@app.route("/create_quiz", methods=["GET", "POST"])
@login_required
def create_quiz(error=None, msg=None, warning=None):
    if session["role"] != "faculty":
        return dashboard(error="Only faculty can create quizzes.")
    
    if request.method == "POST":
        title = request.form.get("title")
        class_no = request.form.get("class_no")
        total_marks = request.form.get("total_marks")
        duration = request.form.get("duration")
        file = request.files.get("file")

        if not file:
            return create_quiz(error="Please upload an Excel file.", msg=None, warning=None)
        if not file.filename.endswith(('.xlsx', '.xls')):
            return create_quiz(error="Invalid file format. Please upload an Excel (.xls or .xlsx) file.", msg=None, warning=None)
        if not title or not class_no or not total_marks or not duration:
            return create_quiz(error="All fields are required.", msg=None, warning=None)
        try:
            # Parse Excel
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            headers = [cell.value for cell in sheet[1]]
            required_headers = ["Question", "A", "B", "C", "D", "Marks", "Minus", "Answer"]
            if headers != required_headers:
                return create_quiz(error="Invalid Excel format. Download the temmplate and try again.", msg=None, warning="Download the template from the link below. <a href='/download_quiz_template'>Download Template</a>")

            questions = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                ques, a, b, c, d, marks, minus, answer = row
                if not ques or not answer:
                    continue
                questions.append({
                    "ques": ques,
                    "a": a,
                    "b": b,
                    "c": c,
                    "d": d,
                    "marks": marks,
                    "minus": minus,
                    "answer": answer
                })

            data_json = json.dumps(questions)

            db.execute(
                "INSERT INTO quizzes (title, class_no, total_marks, duration, data) VALUES (%s, %s, %s, %s, %s)",
                title, class_no, total_marks, duration, data_json
            )

            return dashboard(msg="Quiz created successfully.")

        except Exception as e:
            return create_quiz(error=f"Error parsing file: {e}. Please ensure it follows the correct format or download the template and try again.", msg=None, warning="Download the template from the link below. <a href='/download_quiz_template'>Download Template</a>")
    classes = db.execute("SELECT class_no FROM classrooms WHERE faculty_id = %s", session["user_id"])
    return render_template("create_quiz.html", classes=classes)


@app.route("/download_quiz_template")
@login_required
def download_quiz_template():
    return send_from_directory(
        directory="static/files",
        path="quiz_template.xlsx",
        as_attachment=True
    )



@app.route("/archive", methods=["GET"])
@login_required
def archive():
    q = (request.args.get("q") or "").strip()
    class_no = (request.args.get("class_no") or "").strip()
    sort = (request.args.get("sort") or "newest").strip()

    order_by = "q.quiz_id DESC"
    if sort == "oldest":
        order_by = "q.quiz_id ASC"
    elif sort == "title":
        order_by = "q.title ASC"

    where_parts = ["q.status = 'archive'"]
    params = []

    if session["role"] == "faculty":
        where_parts.append("q.class_no IN (SELECT class_no FROM classrooms WHERE faculty_id = %s)")
        params.append(session["user_id"])
        classes = db.execute(
            "SELECT class_no, COALESCE(nickname, '') AS nickname FROM classrooms WHERE faculty_id = %s ORDER BY class_no",
            session["user_id"],
        )
    elif session["role"] == "student":
        where_parts.append("q.class_no IN (SELECT class_no FROM enrollments WHERE student_id = %s)")
        params.append(session["user_id"])
        classes = db.execute(
            "SELECT c.class_no, COALESCE(c.nickname, '') AS nickname FROM classrooms c JOIN enrollments e ON c.class_no = e.class_no WHERE e.student_id = %s ORDER BY c.class_no",
            session["user_id"],
        )
    else:
        return render_template("dashboard.html", msg="Archive unavailable at the moment.")

    if class_no:
        where_parts.append("q.class_no = %s")
        params.append(class_no)

    if q:
        where_parts.append("(q.title ILIKE %s OR CAST(q.quiz_id AS TEXT) ILIKE %s)")
        like = f"%{q}%"
        params.extend([like, like])

    sql = (
        "SELECT q.*, COALESCE(c.nickname, '') AS class_nickname "
        "FROM quizzes q LEFT JOIN classrooms c ON q.class_no = c.class_no "
        f"WHERE {' AND '.join(where_parts)} "
        f"ORDER BY {order_by}"
    )
    quizzes = db.execute(sql, *params)
    return render_template(
        "archive.html",
        quizzes=quizzes,
        classes=classes,
        q=q,
        selected_class_no=class_no,
        sort=sort,
    )


@app.route("/search", methods=["GET"])
@login_required
def search():
    q = (request.args.get("q") or "").strip()
    if len(q) < 2:
        return jsonify({"results": []})

    like = f"%{q}%"
    results = []

    if session.get("role") == "faculty":
        classes = db.execute(
            "SELECT class_no, COALESCE(nickname, '') AS nickname "
            "FROM classrooms "
            "WHERE faculty_id = %s AND (CAST(class_no AS TEXT) ILIKE %s OR COALESCE(nickname, '') ILIKE %s) "
            "ORDER BY class_no LIMIT 6",
            session["user_id"],
            like,
            like,
        )
        quizzes = db.execute(
            "SELECT quiz_id, title, class_no, status "
            "FROM quizzes "
            "WHERE class_no IN (SELECT class_no FROM classrooms WHERE faculty_id = %s) "
            "AND (title ILIKE %s OR CAST(quiz_id AS TEXT) ILIKE %s) "
            "ORDER BY quiz_id DESC LIMIT 8",
            session["user_id"],
            like,
            like,
        )
    else:
        classes = db.execute(
            "SELECT c.class_no, COALESCE(c.nickname, '') AS nickname "
            "FROM classrooms c JOIN enrollments e ON c.class_no = e.class_no "
            "WHERE e.student_id = %s AND (CAST(c.class_no AS TEXT) ILIKE %s OR COALESCE(c.nickname, '') ILIKE %s) "
            "ORDER BY c.class_no LIMIT 6",
            session["user_id"],
            like,
            like,
        )
        quizzes = db.execute(
            "SELECT q.quiz_id, q.title, q.class_no, q.status "
            "FROM quizzes q JOIN enrollments e ON q.class_no = e.class_no "
            "WHERE e.student_id = %s AND (q.title ILIKE %s OR CAST(q.quiz_id AS TEXT) ILIKE %s) "
            "ORDER BY q.quiz_id DESC LIMIT 8",
            session["user_id"],
            like,
            like,
        )

    for c in classes or []:
        label = c.get("nickname") or "Class"
        results.append(
            {
                "type": "class",
                "title": f"{label}",
                "subtitle": f"Class No: {c.get('class_no')}",
                "url": f"/class/{c.get('class_no')}",
            }
        )

    for qz in quizzes or []:
        status = qz.get("status")
        status_txt = f" • {status}" if status else ""
        results.append(
            {
                "type": "quiz",
                "title": qz.get("title") or f"Quiz {qz.get('quiz_id')}",
                "subtitle": f"Quiz ID: {qz.get('quiz_id')} • Class No: {qz.get('class_no')}{status_txt}",
                "url": f"/quiz/{qz.get('quiz_id')}",
            }
        )

    return jsonify({"results": results[:12]})


@app.route("/quiz/<int:quiz_id>", methods=["GET", "POST"])
@login_required
def quiz_page(quiz_id):
    quiz_rows = db.execute("SELECT * FROM quizzes WHERE quiz_id = %s", quiz_id)
    if not quiz_rows:
        return render_template("dashboard.html", error="Quiz not found.")
    quiz = quiz_rows[0]

    if session["role"] == "student":
        enrollment = db.execute("SELECT * FROM enrollments WHERE class_no = %s AND student_id = %s", quiz["class_no"], session["user_id"])
        if len(enrollment) != 1:
            return render_template("dashboard.html", error="You are not enrolled in this class.")    
    elif session["role"] == "faculty":
        classroom = db.execute("SELECT * FROM classrooms WHERE class_no = %s", quiz["class_no"])
        if classroom[0]["faculty_id"] != session["user_id"]:
            return render_template("dashboard.html", error="You do not have access to this quiz.")

    def _parse_questions(value):
        if value is None or value == "":
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return parsed if isinstance(parsed, list) else []
            except Exception:
                return []
        return []

    questions = _parse_questions(quiz.get("data"))

    scores = db.execute(
        "SELECT qa.*, u.* FROM quiz_attempts qa JOIN users u ON qa.student_id = u.id WHERE qa.quiz_id = %s",
        quiz_id,
    ) or None

    def _to_number(value):
        try:
            if value is None or value == "":
                return 0
            return float(value)
        except Exception:
            return 0

    def _parse_attempt_answers(attempt_row, question_count):
        if not attempt_row:
            return None

        answers_value = attempt_row.get("answers")
        if answers_value is not None and answers_value != "":
            if isinstance(answers_value, list):
                return answers_value
            if isinstance(answers_value, tuple):
                return list(answers_value)
            if isinstance(answers_value, str):
                try:
                    parsed = json.loads(answers_value)
                    return parsed if isinstance(parsed, list) else None
                except Exception:
                    return None

        # Legacy fallback: answer_0, answer_1, ... columns
        legacy = []
        has_any = False
        for i in range(question_count):
            key = f"answer_{i}"
            if key in attempt_row:
                has_any = True
                legacy.append(attempt_row.get(key) or "")

        return legacy if has_any else None

    if request.method == "GET":
        if session["role"] == "faculty":
            return render_template(
                "quiz.html",
                quiz=quiz,
                questions=questions,
                scores=scores,
                attempt=None,
                attempt_answers=None,
            )
        
        elif session["role"] == "student":
            given_attempt_rows = db.execute(
                "SELECT * FROM quiz_attempts WHERE quiz_id = %s AND student_id = %s",
                quiz_id,
                session["user_id"],
            )
            attempt = given_attempt_rows[0] if given_attempt_rows else None
            attempt_answers = _parse_attempt_answers(attempt, len(questions))

            return render_template(
                "quiz.html",
                quiz=quiz,
                questions=questions,
                scores=None,
                attempt=attempt,
                attempt_answers=attempt_answers,
            )
            
    if request.method == "POST":
        if session["role"] == "faculty":
            action = (request.form.get("action") or "toggle_status").strip().lower()

            if action == "toggle_archive":
                if quiz.get("status") == "archive":
                    # Unarchive into a safe inactive state
                    db.execute("UPDATE quizzes SET status = %s WHERE quiz_id = %s", "stopped", quiz_id)
                    quiz = db.execute("SELECT * FROM quizzes WHERE quiz_id = %s", quiz_id)[0]
                    return render_template(
                        "quiz.html",
                        quiz=quiz,
                        questions=questions,
                        scores=scores,
                        attempt=None,
                        attempt_answers=None,
                        msg="Quiz unarchived successfully!",
                    )

                db.execute("UPDATE quizzes SET status = %s WHERE quiz_id = %s", "archive", quiz_id)
                quiz = db.execute("SELECT * FROM quizzes WHERE quiz_id = %s", quiz_id)[0]
                return render_template(
                    "quiz.html",
                    quiz=quiz,
                    questions=questions,
                    scores=scores,
                    attempt=None,
                    attempt_answers=None,
                    msg="Quiz archived successfully!",
                )

            # Default: toggle live/stopped (do not allow when archived)
            if quiz.get("status") == "archive":
                return render_template(
                    "quiz.html",
                    quiz=quiz,
                    questions=questions,
                    scores=scores,
                    attempt=None,
                    attempt_answers=None,
                    warning="Unarchive the quiz to start/stop it.",
                )

            if quiz["status"] == "draft" or quiz["status"] == "stopped":
                db.execute("UPDATE quizzes SET status = %s WHERE quiz_id = %s", "live", quiz_id)
                quiz = db.execute("SELECT * FROM quizzes WHERE quiz_id = %s", quiz_id)[0]
                return render_template(
                    "quiz.html",
                    quiz=quiz,
                    questions=questions,
                    scores=scores,
                    attempt=None,
                    attempt_answers=None,
                    msg="Quiz started successfully!",
                )
            elif quiz["status"] == "live" or quiz["status"] == "active":
                db.execute("UPDATE quizzes SET status = %s WHERE quiz_id = %s", "stopped", quiz_id)
                quiz = db.execute("SELECT * FROM quizzes WHERE quiz_id = %s", quiz_id)[0]
                return render_template(
                    "quiz.html",
                    quiz=quiz,
                    questions=questions,
                    scores=scores,
                    attempt=None,
                    attempt_answers=None,
                    msg="Quiz stopped successfully!",
                )
            return render_template(
                "quiz.html",
                quiz=quiz,
                questions=questions,
                scores=scores,
                attempt=None,
                attempt_answers=None,
                error="Invalid quiz status.",
            )

        # Student submission
        if quiz.get("status") != "live":
            return render_template(
                "quiz.html",
                quiz=quiz,
                questions=questions,
                scores=None,
                attempt=None,
                attempt_answers=None,
                error="Quiz is not live right now.",
            )

        existing_attempt_rows = db.execute(
            "SELECT * FROM quiz_attempts WHERE quiz_id = %s AND student_id = %s",
            quiz_id,
            session["user_id"],
        )
        if existing_attempt_rows:
            attempt = existing_attempt_rows[0]
            attempt_answers = _parse_attempt_answers(attempt, len(questions))
            return render_template(
                "quiz.html",
                quiz=quiz,
                questions=questions,
                scores=None,
                attempt=attempt,
                attempt_answers=attempt_answers,
                warning="You have already attempted this quiz.",
            )

        student_answers = []
        total_score = 0.0
        for i, q in enumerate(questions):
            student_answer = (request.form.get(f"answer_{i}") or "").strip()
            student_answers.append(student_answer)

            correct_answer = (q.get("answer") or "").strip()
            marks = _to_number(q.get("marks"))
            minus = _to_number(q.get("minus"))

            if student_answer and student_answer == correct_answer:
                total_score += marks
            elif student_answer:
                total_score -= minus

        submitted_at = datetime.now()
        db.execute(
            "INSERT INTO quiz_attempts (quiz_id, student_id, score, submitted_at, answers) VALUES (%s, %s, %s, %s, %s)",
            quiz_id,
            session["user_id"],
            total_score,
            submitted_at,
            json.dumps(student_answers),
        )

        attempt = {
            "quiz_id": quiz_id,
            "student_id": session["user_id"],
            "score": total_score,
            "submitted_at": submitted_at,
            "answers": json.dumps(student_answers),
        }
        return render_template(
            "quiz.html",
            quiz=quiz,
            questions=questions,
            scores=None,
            attempt=attempt,
            attempt_answers=student_answers,
            msg="Quiz submitted successfully!",
        )




@app.route("/class/<string:class_no>")
@login_required
def class_page(class_no):
    classroom = db.execute("SELECT * FROM classrooms WHERE class_no = %s", class_no)
    if len(classroom) != 1:
        return render_template("dashboard.html", error="Class not found.")
    elif session["role"] == "student":
        enrollment = db.execute("SELECT * FROM enrollments WHERE class_no = %s AND student_id = %s", class_no, session["user_id"])
        if len(enrollment) != 1:
            return render_template("dashboard.html", error="You are not enrolled in this class.")
    elif session["role"] == "faculty":
        if classroom[0]["faculty_id"] != session["user_id"]:
            return render_template("dashboard.html", error="You do not have access to this class.")
        
    classroom = classroom[0]
    students = db.execute("SELECT users.* FROM users JOIN enrollments ON users.id = enrollments.student_id WHERE enrollments.class_no = %s", class_no)
    quizzes = db.execute("SELECT * FROM quizzes WHERE class_no = %s", class_no)
    return render_template("class.html", classroom=classroom, students=students, quizzes=quizzes, faculty=db.execute("SELECT * FROM users WHERE id = %s", classroom["faculty_id"])[0], current={"role": session["role"], "user_id": session["user_id"]})
    

