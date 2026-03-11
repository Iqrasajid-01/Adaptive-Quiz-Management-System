from flask import Flask, render_template, request, redirect, url_for, session
from models import Learner, DifficultyManager, load_questions
import json, os
import secrets

# Get the directory where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, "templates"),
            static_folder=os.path.join(BASE_DIR, "static"))
app.secret_key = secrets.token_hex(16)  # Generate a secret key for sessions

# ---------------- Data & Setup ----------------
QUESTION_FILE = os.path.join(BASE_DIR, "data", "questions.json")

question_bank = load_questions(QUESTION_FILE)
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

    # Store username in session
    session["username"] = username
    
    # Initialize learner data in session
    session["learner"] = {
        "score": 0,
        "history": [],
        "current_level": "easy",
        "correct_streak": 0
    }
    
    return redirect(url_for("quiz", username=username))

# ---------------- Quiz Page ----------------
@app.route("/quiz/<username>", methods=["GET","POST"])
def quiz(username):
    # Verify username matches session
    if not username or session.get("username") != username:
        return redirect(url_for("index"))

    # Get learner data from session
    learner_data = session.get("learner", {
        "score": 0,
        "history": [],
        "current_level": "easy",
        "correct_streak": 0
    })
    
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

                # Update session data
                session["learner"] = {
                    "history": learner.history,
                    "score": learner.score,
                    "current_level": learner.current_level,
                    "correct_streak": learner.correct_streak
                }

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
    # Verify username matches session
    if not username or session.get("username") != username:
        return redirect(url_for("index"))

    # Get learner data from session
    data = session.get("learner", {
        "score": 0,
        "history": [],
        "current_level": "easy",
        "correct_streak": 0
    })
    
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
