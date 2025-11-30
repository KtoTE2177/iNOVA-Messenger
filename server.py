from flask import Flask, request, jsonify, send_from_directory
import json
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Важно для работы фронтенда!

# Хранилище данных в памяти (в продакшене используйте БД)
users = []
messages = []
private_messages = []

# Файлы для постоянного хранения (опционально)
USERS_FILE = 'users.json'
MESSAGES_FILE = 'messages.json'

def load_data():
    global users, messages
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                users = json.load(f)
        if os.path.exists(MESSAGES_FILE):
            with open(MESSAGES_FILE, 'r') as f:
                messages = json.load(f)
    except:
        pass

def save_data():
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f)
    except:
        pass

# Загружаем данные при старте
load_data()

# Статические файлы
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# API Endpoints
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        print(f"Регистрация: {username}")
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Проверка существующего пользователя
        if any(user['username'] == username for user in users):
            return jsonify({'error': 'User already exists'}), 409
        
        # Создаем нового пользователя
        new_user = {
            'id': len(users) + 1,
            'username': username,
            'password': password,  # В реальном приложении хешируйте пароль!
            'created_at': datetime.now().isoformat(),
            'avatar': None,
            'aboutMe': ''
        }
        users.append(new_user)
        save_data()
        
        return jsonify({
            'message': 'User registered successfully', 
            'userId': new_user['id'],
            'username': new_user['username']
        }), 201
        
    except Exception as e:
        print(f"Ошибка регистрации: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        print(f"Вход: {username}")
        
        # Ищем пользователя
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

# Получение всех сообщений
@app.route('/api/messages', methods=['GET'])
def get_messages():
    try:
        return jsonify(messages)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Отправка сообщения
@app.route('/api/messages', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        text = data.get('text')
        username = data.get('username')
        replyToId = data.get('replyToId')
        
        print(f"Отправка сообщения: {username} - {text}")
        
        if not text or not username:
            return jsonify({'error': 'Text and username are required'}), 400
        
        # Создаем новое сообщение
        new_message = {
            'id': len(messages) + 1,
            'text': text,
            'username': username,
            'timestamp': datetime.now().isoformat(),
            'replyToId': replyToId,
            'isFavorite': False,
            'editedTimestamp': None
        }
        
        messages.append(new_message)
        save_data()
        
        return jsonify({'success': True, 'message': new_message})
        
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")
        return jsonify({'error': str(e)}), 500

# Избранные сообщения
@app.route('/api/messages/favorites', methods=['GET'])
def get_favorite_messages():
    try:
        favorite_messages = [msg for msg in messages if msg.get('isFavorite')]
        return jsonify(favorite_messages)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Добавление/удаление из избранного
@app.route('/api/message/favorite', methods=['POST'])
def toggle_favorite():
    try:
        data = request.get_json()
        message_id = data.get('messageId')
        is_favorite = data.get('isFavorite')
        
        message = next((msg for msg in messages if msg['id'] == message_id), None)
        if message:
            message['isFavorite'] = is_favorite
            save_data()
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Message not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Редактирование сообщения
@app.route('/api/message/edit', methods=['POST'])
def edit_message():
    try:
        data = request.get_json()
        message_id = data.get('messageId')
        new_text = data.get('newText')
        
        message = next((msg for msg in messages if msg['id'] == message_id), None)
        if message:
            message['text'] = new_text
            message['editedTimestamp'] = datetime.now().isoformat()
            save_data()
            return jsonify({'success': True, 'editedTimestamp': message['editedTimestamp']})
        else:
            return jsonify({'error': 'Message not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Поиск пользователей
@app.route('/api/users/search', methods=['GET'])
def search_users():
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify([])
        
        filtered_users = [
            user for user in users 
            if query in user['username'].lower() and user['username'] != 'current_user'  # Исключаем текущего пользователя
        ]
        return jsonify(filtered_users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Получение всех пользователей
@app.route('/api/users', methods=['GET'])
def get_all_users():
    try:
        # Возвращаем всех пользователей кроме текущего (если нужно)
        return jsonify([user for user in users if user['username'] != 'current_user'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Приватные сообщения
@app.route('/api/private-messages', methods=['GET'])
def get_private_messages():
    try:
        username = request.args.get('username')
        # Здесь должна быть логика для приватных сообщений
        # Пока возвращаем пустой список
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/private-message', methods=['POST'])
def send_private_message():
    try:
        data = request.get_json()
        # Здесь должна быть логика для отправки приватных сообщений
        return jsonify({'success': True, 'message': 'Private message sent'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'users_count': len(users), 'messages_count': len(messages)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
