import json

def safe(value):
    if isinstance(value, str):
        return value.replace("'", "''").replace("\n", "\\n").replace("{","{{").replace("}","}}")
    return value

data = json.load(open("data/questions.json", "r", encoding="utf-8"))

with open("insert_questions.sql", "w", encoding="utf-8") as f:
    for q in data:
        sql = f"""
INSERT INTO Questions (id, difficulty, question, options, answer)
VALUES (
    {q['id']},
    '{safe(q['difficulty'])}',
    '{safe(q['question'])}',
    '{safe(json.dumps(q['options']))}',
    '{safe(q['answer'])}'
);
"""
        f.write(sql)
