from flask import Flask, render_template, request, redirect, url_for
from models import Learner, DifficultyManager, load_questions, load_learners, save_learners
import json, os
from datetime import datetime
import pyodbc

app = Flask(__name__)

# ---------------- Data & Setup ----------------
QUESTION_FILE = "data/questions.json"
LEARNERS_FILE = "data/learners.json"
LOG_FILE = "data/logs.json"

question_bank = load_questions(QUESTION_FILE)
learners = load_learners(LEARNERS_FILE)
dm = DifficultyManager()

# ---------------- Home Page ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- Start Quiz ----------------
@app.route("/start", methods=["POST"])
def start_quiz():
    username = request.form.get("username", "").strip()
    if not username:
        return redirect(url_for("index"))

    # Reset learner data for a fresh session
    learners[username] = {
        "score": 0,
        "history": [],
        "current_level": "easy",
        "correct_streak": 0
    }
    save_learners(learners)
    return redirect(url_for("quiz", username=username))

# ---------------- Quiz Page ----------------
@app.route("/quiz/<username>", methods=["GET","POST"])
def quiz(username):
    if not username or username not in learners:
        return redirect(url_for("index"))

    # Load learner data
    learner_data = learners[username]
    learner = Learner(username)
    learner.history = learner_data.get("history", [])
    learner.score = learner_data.get("score", 0)
    learner.current_level = learner_data.get("current_level", "easy")
    learner.correct_streak = learner_data.get("correct_streak", 0)

    # Handle POST: Answer submission
    if request.method == "POST":
        qid_str = request.form.get("question_id")
        selected = request.form.get("option")
        if qid_str and selected:
            qid = int(qid_str)
            q = next((item for item in question_bank if item["id"] == qid), None)
            if q:
                correct = selected == q["answer"]
                learner.record_attempt(qid, correct, q["difficulty"])

                # Save logs safely
                logs = []
                if os.path.exists(LOG_FILE):
                    try:
                        with open(LOG_FILE, "r") as f:
                            logs = json.load(f)
                    except:
                        logs = []
                logs.append({
                    "timestamp": str(datetime.now()),
                    "learner": username,
                    "question_id": qid,
                    "selected": selected,
                    "correct": correct,
                    "difficulty": q["difficulty"]
                })
                with open(LOG_FILE, "w") as f:
                    json.dump(logs, f, indent=4)

                # Update learners dict & save
                learners[username]["history"] = learner.history
                learners[username]["score"] = learner.score
                learners[username]["current_level"] = learner.current_level
                learners[username]["correct_streak"] = learner.correct_streak
                save_learners(learners)

    # Get next question adaptively
    next_q = dm.next_question(learner, question_bank)
    if not next_q:
        return redirect(url_for("dashboard", username=username))

    # Pass streak and current level to template
    return render_template(
        "quiz.html",
        question=next_q,
        username=username,
        score=learner.score,
        current_level=learner.current_level,
        correct_streak=learner.correct_streak
    )

# ---------------- Dashboard ----------------
@app.route("/dashboard/<username>")
def dashboard(username):
    if username not in learners:
        return redirect(url_for("index"))

    data = learners[username]
    history = data.get("history", [])
    total = len(history)
    correct = sum(1 for h in history if h.get("correct"))
    accuracy = round((correct / total) * 100, 2) if total > 0 else 0

    # Difficulty distribution
    dist = {"easy": 0, "medium": 0, "hard": 0}
    for h in history:
        d = h.get("difficulty")
        if d in dist:
            dist[d] += 1

    # Calculate cumulative score progress
    score_progress = []
    cumulative = 0
    for h in history:
        if h.get("correct"):
            cumulative += 1
        score_progress.append(cumulative)

    # ---------------- FIX: Pass history to template for chart ----------------
    return render_template(
        "dashboard.html",
        username=username,
        score=data.get("score", 0),
        total=total,
        correct=correct,
        accuracy=accuracy,
        dist=dist,
        current_level=data.get("current_level", "easy"),
        correct_streak=data.get("correct_streak", 0),
        history=history,
        score_progress=score_progress
    )

if __name__ == "__main__":
    app.run(debug=True)

# For Vercel deployment
app = app
