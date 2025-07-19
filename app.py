from urllib.parse import quote_plus
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
username = quote_plus(os.getenv("USERNAME"))
password = quote_plus(os.getenv("PASSWORD"))
# MongoDB setup
client = MongoClient(f"mongodb+srv://{username}:{password}@dhanu.yxabe4w.mongodb.net/?retryWrites=true&w=majority&appName=Dhanu")
db = client["todo_db"]
todos = db["todos"]

# Display all tasks
@app.route("/")
def index():
    all_todos = list(todos.find())
    return render_template("index.html", todos=all_todos)

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
    app.run(debug=True)
