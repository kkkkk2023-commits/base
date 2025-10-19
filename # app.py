# app.py
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from database import init_db, get_user, update_device_fingerprint
from questions import QUESTIONS
import hashlib

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Инициализация БД при запуске
init_db()

def get_device_fingerprint():
    ua = request.headers.get('User-Agent', '')
    screen = request.args.get('screen', 'unknown')
    platform = request.args.get('platform', 'unknown')
    return hashlib.sha256(f"{ua}{screen}{platform}".encode()).hexdigest()[:16]

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    fp = get_device_fingerprint()

    user = get_user(email)
    if not user:
        return "❌ Пользователь не найден", 403

    from werkzeug.security import check_password_hash
    if not check_password_hash(user['password_hash'], password):
        return "❌ Неверный пароль", 403

    # Проверка устройства
    if user['device_fingerprint'] and user['device_fingerprint'] != fp:
        return "🔒 Доступ разрешён только с зарегистрированного устройства", 403

    # Сохраняем fingerprint при первом входе
    if not user['device_fingerprint']:
        update_device_fingerprint(user['id'], fp)

    session['user_id'] = user['id']
    session['email'] = user['email']
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', email=session['email'], topics=QUESTIONS.keys())

@app.route('/get_questions')
def get_questions():
    if 'user_id' not in session:
        return jsonify([]), 403
    topic = request.args.get('topic')
    if topic in QUESTIONS:
        return jsonify(QUESTIONS[topic])
    return jsonify([])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)