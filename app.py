from flask import Flask, request, render_template, redirect, session, jsonify
import sqlite3, os

app = Flask(__name__)
app.secret_key = "budilab-secret"

DB_PATH = "instance/budilab.db"
os.makedirs("instance", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)

def db():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

if not os.path.exists(DB_PATH):
    conn = db()
    conn.executescript("""
    CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT);
    CREATE TABLE notes(id INTEGER PRIMARY KEY, user_id INTEGER, content TEXT);
    INSERT INTO users(username,password,role) VALUES('admin','admin123','admin');
    """)
    conn.commit()
    conn.close()

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        q = f"SELECT * FROM users WHERE username='{u}' AND password='{p}'"
        user = db().execute(q).fetchone()
        if user:
            session["uid"] = user["id"]
            session["role"] = user["role"]
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        db().execute(f"INSERT INTO users(username,password,role) VALUES('{u}','{p}','user')")
        db().commit()
        return redirect("/")
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    uid = session.get("uid")
    notes = db().execute(f"SELECT * FROM notes WHERE user_id={uid}").fetchall()
    return render_template("dashboard.html", notes=notes)

@app.route("/profile")
def profile():
    uid = request.args.get("id")
    user = db().execute(f"SELECT * FROM users WHERE id={uid}").fetchone()
    return render_template("profile.html", user=user)

@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return "Forbidden"
    users = db().execute("SELECT * FROM users").fetchall()
    return render_template("admin.html", users=users)

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    path = f"static/uploads/{f.filename}"
    f.save(path)
    return path

@app.route("/api/users")
def api_users():
    return jsonify([dict(u) for u in db().execute("SELECT * FROM users")])

app.run(host="0.0.0.0", port=5001, debug=True)

