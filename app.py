from urllib.parse import quote_plus
from flask import Flask, render_template, request, redirect, url_for,session,flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET")
bcrypt = Bcrypt(app)

username = quote_plus(os.getenv("USERNAME"))
password = quote_plus(os.getenv("PASSWORD"))
# MongoDB setup
client = MongoClient(f"mongodb+srv://kiran:{password}@cluster0.aotevze.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",authSource="admin")
db = client["todo_db"]
todos = db["todos"]
users = db["users"]

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        if users.find_one({'email': email}):
            flash('Email already registered.', 'warning')
            return redirect(url_for('register'))

        users.insert_one({'email': email, 'password': password})
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_input = request.form['password']

        user = users.find_one({'email': email})
        if user and bcrypt.check_password_hash(user['password'], password_input):
            session['user_id'] = str(user['_id'])
            session['email'] = user['email']
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Display all tasks
@app.route("/")
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    
    user_id = session['user_id']
    user_todos = list(todos.find())
    # Create serializer like Flask does
    serializer = URLSafeTimedSerializer(os.getenv("SECRET"))

    # Your session cookie value (copied from the browser)
    session_cookie =user_id

    # Decode
    try:
        data = serializer.loads(session_cookie, salt='cookie-session')
        print("Decoded session data:", data)
    except Exception as e:
        print("Failed to decode:", e)
    return render_template('index.html', todos=user_todos, email=session['email'])

# Add a task
@app.route("/add", methods=["POST"])
def add():
    task = request.form.get("task")
    if task:
        todos.insert_one({"task": task, "done": False})
    return redirect(url_for("index"))

# Toggle done/undone
@app.route("/toggle/<id>")
def toggle(id):
    todo = todos.find_one({"_id": ObjectId(id)})
    todos.update_one({"_id": ObjectId(id)}, {"$set": {"done": not todo["done"]}})
    return redirect(url_for("index"))

# Delete a task
@app.route("/delete/<id>")
def delete(id):
    todos.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run()
