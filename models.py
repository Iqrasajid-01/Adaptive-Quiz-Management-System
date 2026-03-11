# models.py
import json
import random
from datetime import datetime

class Question:
    def __init__(self, id, question, options, answer, difficulty):
        self.id = id
        self.question = question
        self.options = options
        self.answer = answer
        self.difficulty = difficulty

class Learner:
    def __init__(self, username):
        self.username = username
        self.history = []  # list of dicts {question_id, correct, difficulty, timestamp}
        self.score = 0
        self.current_level = "easy"  # default starting level
        self.correct_streak = 0      # to track consecutive correct answers

    def record_attempt(self, question_id, correct, difficulty):
        """Record learner's attempt and update score, streak and level"""
        self.history.append({
            "question_id": question_id,
            "correct": correct,
            "difficulty": difficulty,
            "timestamp": str(datetime.now())
        })

        # Update score
        if correct:
            self.score += 1
            self.correct_streak += 1
        else:
            self.correct_streak = 0  # reset streak on wrong answer

        # Adaptive level logic
        levels = ["easy", "medium", "hard"]
        idx = levels.index(self.current_level)

        if self.correct_streak >= 3:  # 3 correct answers in a row → upgrade level
            if idx < len(levels) - 1:
                self.current_level = levels[idx + 1]
                self.correct_streak = 0  # reset streak after upgrade
        elif not correct:  # wrong answer → downgrade level if not already easy
            if idx > 0:
                self.current_level = levels[idx - 1]
                self.correct_streak = 0

class DifficultyManager:
    def __init__(self):
        self.levels = ["easy", "medium", "hard"]

    def next_question(self, learner, question_bank):
        """Return a random question for learner based on current level"""
        # Filter questions for learner's current level
        filtered = [q for q in question_bank if q['difficulty'] == learner.current_level]
        if filtered:
            return random.choice(filtered)
        elif question_bank:
            # fallback: pick any question if none in current level
            return random.choice(question_bank)
        else:
            return None

# ------------------- Utility Functions -------------------

def load_questions(file_path="data/questions.json"):
    """Load questions from JSON file"""
    with open(file_path, "r") as f:
        return json.load(f)

def load_learners(file_path="data/learners.json"):
    """Load learners from JSON file"""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except:
        return {}

def save_learners(learners, file_path="data/learners.json"):
    """Save learners data to JSON file"""
    with open(file_path, "w") as f:
        json.dump(learners, f, indent=4)
