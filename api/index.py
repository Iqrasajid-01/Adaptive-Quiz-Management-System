from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import secrets
import random
from datetime import datetime
import sys
import traceback

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

print(f"[DEBUG] BASE_DIR: {BASE_DIR}", file=sys.stderr)
print(f"[DEBUG] ROOT_DIR: {ROOT_DIR}", file=sys.stderr)

app = Flask(__name__,
            template_folder=os.path.join(ROOT_DIR, "templates"),
            static_folder=os.path.join(ROOT_DIR, "static"))
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))

# ---------------- Data & Setup ----------------
def load_questions_from_file(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def get_question_bank():
    try:
        question_file = os.path.join(ROOT_DIR, "data", "questions.json")
        print(f"[DEBUG] Loading questions from: {question_file}", file=sys.stderr)
        print(f"[DEBUG] File exists: {os.path.exists(question_file)}", file=sys.stderr)
        print(f"[DEBUG] ROOT_DIR contents: {os.listdir(ROOT_DIR)}", file=sys.stderr)
        if os.path.exists(os.path.join(ROOT_DIR, "data")):
            print(f"[DEBUG] data/ contents: {os.listdir(os.path.join(ROOT_DIR, "data"))}", file=sys.stderr)
        questions = load_questions_from_file(question_file)
        print(f"[DEBUG] Loaded {len(questions)} questions", file=sys.stderr)
        return questions
    except Exception as e:
        print(f"[ERROR] Error loading questions: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return []

def get_next_question(question_bank, current_level):
    levels = ["easy", "medium", "hard"]
    filtered = [q for q in question_bank if q.get('difficulty') == current_level]
    if filtered:
        return random.choice(filtered)
    elif question_bank:
        return random.choice(question_bank)
    else:
        return None

# Initialize
question_bank = get_question_bank()

# ---------------- Routes ----------------
@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        return f"<h1>Error</h1><pre>{str(e)}\n\n{traceback.format_exc()}</pre>", 500

@app.route("/start", methods=["POST"])
def start_quiz():
    try:
        username = request.form.get("username", "").strip()
        if not username:
            return redirect(url_for("index"))
        session["username"] = username
        session["learner"] = {
            "score": 0,
            "history": [],
            "current_level": "easy",
            "correct_streak": 0
        }
        return redirect(url_for("quiz", username=username))
    except Exception as e:
        return f"<h1>Error</h1><pre>{str(e)}\n\n{traceback.format_exc()}</pre>", 500

@app.route("/quiz/<username>", methods=["GET","POST"])
def quiz(username):
    try:
        if not username or session.get("username") != username:
            return redirect(url_for("index"))
        
        learner_data = session.get("learner", {
            "score": 0,
            "history": [],
            "current_level": "easy",
            "correct_streak": 0
        })
        
        current_level = learner_data.get("current_level", "easy")
        correct_streak = learner_data.get("correct_streak", 0)
        score = learner_data.get("score", 0)
        history = learner_data.get("history", [])
        
        if request.method == "POST":
            qid_str = request.form.get("question_id")
            selected = request.form.get("option")
            if qid_str and selected:
                qid = int(qid_str)
                q = next((item for item in question_bank if item["id"] == qid), None)
                if q:
                    correct = selected == q["answer"]
                    if correct:
                        score += 1
                        correct_streak += 1
                    else:
                        correct_streak = 0
                    
                    levels = ["easy", "medium", "hard"]
                    idx = levels.index(current_level)
                    if correct_streak >= 3:
                        if idx < len(levels) - 1:
                            current_level = levels[idx + 1]
                            correct_streak = 0
                    elif not correct:
                        if idx > 0:
                            current_level = levels[idx - 1]
                            correct_streak = 0
                    
                    history.append({
                        "question_id": qid,
                        "correct": correct,
                        "difficulty": q["difficulty"],
                        "timestamp": str(datetime.now())
                    })
                    
                    session["learner"] = {
                        "history": history,
                        "score": score,
                        "current_level": current_level,
                        "correct_streak": correct_streak
                    }
        
        if not question_bank:
            return "<h1>Error</h1><p>No questions available</p>", 500
            
        next_q = get_next_question(question_bank, current_level)
        if not next_q:
            return redirect(url_for("dashboard", username=username))
        
        return render_template(
            "quiz.html",
            question=next_q,
            username=username,
            score=score,
            current_level=current_level,
            correct_streak=correct_streak
        )
    except Exception as e:
        return f"<h1>Error</h1><pre>{str(e)}\n\n{traceback.format_exc()}</pre>", 500

@app.route("/dashboard/<username>")
def dashboard(username):
    try:
        if not username or session.get("username") != username:
            return redirect(url_for("index"))
        
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
        
        dist = {"easy": 0, "medium": 0, "hard": 0}
        for h in history:
            d = h.get("difficulty")
            if d in dist:
                dist[d] += 1
        
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
    except Exception as e:
        return f"<h1>Error</h1><pre>{str(e)}\n\n{traceback.format_exc()}</pre>", 500

def handler(request):
    return app(request.environ, lambda *args: None)
