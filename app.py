from flask import Flask, render_template, request, redirect, flash , session , url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = '123'

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',        # or your database IP
        user='root',
        password='jim@1010',
        database='trustdb'
    )

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pow_trust WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            if user and user['role'] in {"chairman", "secretary"}:
                session["username"] = user["username"]
                session["role"] = user["role"]
                flash("✅ Login Successful")
                return redirect("/dashboard")
            else:
                flash("❌ access denied: you are not authorized to login")
                return redirect("/login")
        else:
            flash("❌ Invalid username or password")
            return redirect("/login")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "username" in session and session["role"] in ["chairman", "secretary"]:
        return render_template("dashboard.html")
    else:
        flash("Access denied.")
        return redirect("/login")

@app.route("/edit_notice", methods=["GET", "POST"])
def edit_notice():
    if 'role' not in session or session['role'] not in ['chairman', 'secretary']:
        return "Access Denied", 403

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        new_notice = request.form["content"]
        cursor.execute("INSERT INTO notice (content) VALUES (%s)", (new_notice,))
        conn.commit()
        conn.close()
        flash("Notice updated successfully!")
        return redirect(url_for("show_notice"))

    # Fetch current notice
    cursor.execute("SELECT content FROM notice ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    current_notice = result[0] if result else ""
    return render_template("edit_notice.html", content=current_notice)

@app.route("/edit_events")
def edit_events():
    if "username" in session and session["role"] in ["chairman", "secretary"]:
        # Fetch events data
        return render_template("edit_events.html")
    else:
        flash("Access denied.")
        return redirect("/login")

@app.route('/search_member', methods=['GET', 'POST'])
def search_member():
    member = None

    if request.method == 'POST':
        name = request.form['name']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM members WHERE name = %s", (name,))
        member = cursor.fetchone()

        conn.close()

    return render_template("search_member.html", member=member)
    
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect("/")

@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/notice")
def show_notice():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM notice ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    notice_text = result[0] if result else "No notice yet."
    return render_template("notice.html", notice=notice_text)

@app.route('/events')
def events():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
    events = cursor.fetchall()

    conn.close()

    return render_template("events.html", events=events)

@app.route('/mission')
def mission():
    return render_template("mission.html")

@app.route('/members')
def members():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM members ORDER BY position ASC")
    members = cursor.fetchall()

    conn.close()

    return render_template("members.html", members=members)

@app.route('/address')
def address():
    address_text="5a1a1, rs muthu nagar,papanasam,tamil nadu"
    return render_template("address.html",address=address_text)

@app.route('/manage_events')
def manage_events():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
    events = cursor.fetchall()

    conn.close()

    return render_template("manage_events.html", events=events)

@app.route('/add_event', methods=['GET','POST'])
def add_event():
    if request.method == 'POST':
        date = request.form['date']
        name = request.form['name']
        time = request.form['time']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (event_date, event_name, event_time) VALUES (%s,%s,%s)",
            (date, name, time)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('manage_events'))

    return render_template("add_event.html")

@app.route('/edit_event/<int:id>', methods=['GET','POST'])
def edit_event(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        date = request.form['date']
        name = request.form['name']
        time = request.form['time']

        cursor.execute(
            "UPDATE events SET event_date=%s, event_name=%s, event_time=%s WHERE id=%s",
            (date, name, time, id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('manage_events'))

    cursor.execute("SELECT * FROM events WHERE id=%s", (id,))
    event = cursor.fetchone()
    conn.close()

    return render_template("edit_event.html", event=event)

@app.route('/delete_event/<int:id>')
def delete_event(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('manage_events'))

@app.route('/feedback')
def feedback():
    return render_template('feedback.html',success=True)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO feedback (name, email, message) VALUES (%s, %s, %s)",
        (name, email, message)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('feedback'))

@app.route('/view_feedbacks')
def view_feedbacks():
    if "username" in session and session["role"] in ["chairman", "secretary"]:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM feedback ORDER BY created_at ASC")
        feedbacks = cursor.fetchall()

        conn.close()

        return render_template("view_feedbacks.html", feedbacks=feedbacks)
    else:
        flash("Access denied")
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=10000)
