from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'VeryStrongKey'

def get_db_connection():
    conn = sqlite3.connect('quiz.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_question_after(question_id=0, quiz_id=1):
    conn = get_db_connection()
    cursor = conn.cursor()

    if question_id == 0:
        cursor.execute('''
        SELECT question.id, question.text, question.true, question.false1, question.false2, question.false3
        FROM question
        JOIN quiz_content ON question.id = quiz_content.question_id
        WHERE quiz_content.quiz_id = ?
        ORDER BY question.id ASC
        LIMIT 1
        ''', (quiz_id,))

    else:
        cursor.execute('''
        SELECT question.id, question.text, question.true, question.false1, question.false2, question.false3
        FROM question
        JOIN quiz_content ON question.id = quiz_content.question_id
        WHERE quiz_content.quiz_id = ? AND question.id > ?
        ORDER BY question.id ASC
        LIMIT 1
        ''', (quiz_id, question_id))

    row = cursor.fetchone()
    conn.close()
    if row:
        answers = [row["true"], row["false1"], row["false2"], row["false3"]]
        random.shuffle(answers)
        return {
            'id': row["id"],
            'text': row["text"],
            'answers': answers,
            'correct': row["true"]
        }
    else:
        return None

@app.route('/')
def index():
    conn = get_db_connection()
    quizzes = conn.execute('SELECT id, title FROM quiz').fetchall()
    conn.close()
    return render_template('index.html', quizzes=quizzes)

@app.route('/test/<quiz_id>', methods=['GET', 'POST'])
def test(quiz_id):
    if 'score' not in session:
        session['score'] = 0
    if 'question_id' not in session:
        session['question_id'] = 0
    if 'quiz_id' not in session:
        session['quiz_id'] = quiz_id

    if request.method == 'POST':
        selected_answer = request.form.get('answer')
        correct_answer = session.get('correct')
        if selected_answer == correct_answer:
            session['score'] += 1

    question = get_question_after(session['question_id'], quiz_id)
    if question:
        session['question_id'] = question['id']
        session['correct'] = question['correct']
        return render_template('test.html', question=question)
    else:
        result = session['score']
        session.clear()
        return redirect(url_for('result', score=result))

@app.route('/result')
def result():
    score = request.args.get('score', 0)
    return render_template('result.html', score=score)

if __name__ == '__main__':
    app.run()