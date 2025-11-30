from flask import Flask, request, jsonify, render_template
import json
import os
from datetime import datetime

app = Flask(__name__)

# Файл для хранения данных
USERS_FILE = 'users.json'
MESSAGES_FILE = 'messages.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def load_messages():
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_messages(messages):
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# API для регистрации
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        print(f"Регистрация: {username}")  # Для отладки
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        users = load_users()
        
        # Проверка существующего пользователя
        if any(user['username'] == username for user in users):
            return jsonify({'error': 'User already exists'}), 409
        
        # Добавление нового пользователя
        new_user = {
            'id': len(users) + 1,
            'username': username,
            'password': password,  # В реальном приложении нужно хешировать!
            'created_at': datetime.now().isoformat()
        }
        users.append(new_user)
        save_users(users)
        
        return jsonify({
            'message': 'User registered successfully', 
            'userId': new_user['id'],
            'username': new_user['username']
        }), 201
        
    except Exception as e:
        print(f"Ошибка регистрации: {e}")
        return jsonify({'error': str(e)}), 500

# API для входа
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        print(f"Вход: {username}")  # Для отладки
        
        users = load_users()
        
        # Поиск пользователя
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        
        if user:
            return jsonify({
                'message': 'Login successful', 
                'userId': user['id'],
                'username': user['username']
            })
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
            
    except Exception as e:
        print(f"Ошибка входа: {e}")
        return jsonify({'error': str(e)}), 500

# API для получения сообщений
@app.route('/api/messages', methods=['GET'])
def get_messages():
    try:
        messages = load_messages()
        return jsonify(messages)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API для отправки сообщений
@app.route('/api/messages', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        username = data.get('username')
        message = data.get('message')
        
        if not username or not message:
            return jsonify({'error': 'Username and message are required'}), 400
        
        messages = load_messages()
        new_message = {
            'id': len(messages) + 1,
            'username': username,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        messages.append(new_message)
        save_messages(messages)
        
        return jsonify({'message': 'Message sent successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Создаем файлы если их нет
    if not os.path.exists(USERS_FILE):
        save_users([])
    if not os.path.exists(MESSAGES_FILE):
        save_messages([])
    
    app.run(debug=True, port=5000)
