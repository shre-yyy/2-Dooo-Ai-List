from flask import Flask, render_template, request, redirect, jsonify
import sqlite3, random
from datetime import date
try:
    from utils.ai import generate_plan_ai, generate_suggestions_ai
    AI_ENABLED = True
except:
    AI_ENABLED = False

app = Flask(__name__)

def db():
    return sqlite3.connect("todo.db")

# DB init
conn = db()
conn.execute("""
CREATE TABLE IF NOT EXISTS tasks(
id INTEGER PRIMARY KEY AUTOINCREMENT,
task TEXT,
date TEXT,
time TEXT,
priority TEXT,
status TEXT)
""")
conn.close()


quotes = [
"Discipline beats motivation.",
"Small steps every day.",
"Consistency wins.",
"Focus creates success."
]

@app.route('/')
def home():
    selected_date = request.args.get('date')

    if not selected_date:
        selected_date = date.today().isoformat()

    conn = db()
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE date=?",
        (selected_date,)
    ).fetchall()
    conn.close()

    total = len(tasks)
    done = len([t for t in tasks if t[4] == "done"])
    score = int((done/total)*100) if total > 0 else 0

    return render_template("index.html",
        tasks=tasks,
        selected_date=selected_date,
        score=score
    )


@app.route('/add', methods=['POST'])
def add():
    t = request.form['task']
    date = request.form['date']
    time = request.form['time']
    priority = request.form['priority']

    conn = db()
    conn.execute(
        "INSERT INTO tasks(task,date,time,priority,status) VALUES(?,?,?,?,?)",
        (t, date, time, priority, "pending")
    )
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/delete/<int:id>')
def delete(id):
    conn = db()
    conn.execute("DELETE FROM tasks WHERE id=?",(id,))
    conn.commit(); conn.close()
    return redirect('/')

@app.route('/complete/<int:id>')
def complete(id):
    conn = db()
    conn.execute("UPDATE tasks SET status='done' WHERE id=?",(id,))
    conn.commit(); conn.close()
    return redirect('/')

@app.route('/ai-plan')
def ai_plan():
    conn = db()
    data = conn.execute("SELECT task, priority FROM tasks").fetchall()
    conn.close()

    if AI_ENABLED:
        try:
            plan = generate_plan_ai(data)
        except:
            plan = fallback(data)
    else:
        plan = fallback(data)

    return jsonify({"plan": plan})


@app.route('/ai-suggestions')
def ai_suggestions():
    conn = db()
    tasks = [t[0] for t in conn.execute("SELECT task FROM tasks").fetchall()]
    conn.close()

    if AI_ENABLED:
        try:
            sug = generate_suggestions_ai(tasks)
        except:
            sug = fallback_suggestions(tasks)
    else:
        sug = fallback_suggestions(tasks)

    return jsonify({"suggestions": sug})

def fallback(tasks):
    plan=""
    t=9

    # Sort: High → Medium → Low
    tasks = sorted(tasks, key=lambda x: {"High":0,"Medium":1,"Low":2}.get(x[1],3))

    for task, priority in tasks:
        plan += f"{t}:00 - {task} ({priority})\n"
        t += 1

    return plan


def fallback_suggestions(tasks):
    s=""
    if len(tasks)>5: s+="⚠️ Too many tasks\n"
    if len(tasks)==0: s+="Add tasks to begin\n"
    s+="✅ Do important tasks first\n⏰ Take breaks"
    return s

if __name__ == "__main__":
    app.run()
