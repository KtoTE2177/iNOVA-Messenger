from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Разрешаем запросы с фронтенда

# Файлы для хранения данных
USERS_FILE = 'users.json'
MESSAGES_FILE = 'messages.json'
PRIVATE_MESSAGES_FILE = 'private_messages.json'

def load_users():
    """Загружаем пользователей из файла"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading users: {e}")
    return []

def save_users(users_list):
    """Сохраняем пользователей в файл"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_list, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving users: {e}")

def load_messages():
    """Загружаем сообщения из файла"""
    try:
        if os.path.exists(MESSAGES_FILE):
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading messages: {e}")
    return []

def save_messages(messages_list):
    """Сохраняем сообщения в файл"""
    try:
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages_list, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving messages: {e}")

def load_private_messages():
    """Загружаем приватные сообщения из файла"""
    try:
        if os.path.exists(PRIVATE_MESSAGES_FILE):
            with open(PRIVATE_MESSAGES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading private messages: {e}")
    return []

def save_private_messages(messages_list):
    """Сохраняем приватные сообщения в файл"""
    try:
        with open(PRIVATE_MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages_list, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving private messages: {e}")

# Инициализация данных
users = load_users()
messages = load_messages()
private_messages = load_private_messages()

# Статические файлы
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# Регистрация пользователя
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        print(f"Регистрация: {username}")
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
            
        if len(password) < 4:
            return jsonify({'error': 'Password must be at least 4 characters'}), 400
        
        # Загружаем актуальных пользователей
        current_users = load_users()
        
        # Проверка существующего пользователя
        if any(user['username'] == username for user in current_users):
            return jsonify({'error': 'User already exists'}), 409
        
        # Создаем нового пользователя
        new_user = {
            'id': len(current_users) + 1,
            'username': username,
            'password': password,
            'created_at': datetime.now().isoformat(),
            'avatar': None,
            'aboutMe': '',
            'status': 'online'
        }
        
        current_users.append(new_user)
        save_users(current_users)
        
        # Обновляем глобальную переменную
        global users
        users = current_users
        
        print(f"Пользователь зарегистрирован: {username}, всего пользователей: {len(current_users)}")
        
        return jsonify({
            'message': 'User registered successfully', 
            'userId': new_user['id'],
            'username': new_user['username']
        }), 201
        
    except Exception as e:
        print(f"Ошибка регистрации: {e}")
        return jsonify({'error': str(e)}), 500

# Вход пользователя
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        print(f"Вход: {username}")
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Загружаем актуальных пользователей
        current_users = load_users()
        print(f"Всего пользователей в системе: {len(current_users)}")
        print("Доступные пользователи:", [u['username'] for u in current_users])
        
        # Ищем пользователя
        user = next((u for u in current_users if u['username'] == username and u['password'] == password), None)
        
        if user:
            print(f"Успешный вход: {username}")
            
            # Обновляем статус пользователя
            user['status'] = 'online'
            save_users(current_users)
            
            return jsonify({
                'message': 'Login successful', 
                'userId': user['id'],
                'username': user['username']
            })
        else:
            print(f"Неверные учетные данные: {username}")
            return jsonify({'error': 'Invalid username or password'}), 401
            
    except Exception as e:
        print(f"Ошибка входа: {e}")
        return jsonify({'error': str(e)}), 500

# Получение всех сообщений
@app.route('/api/messages', methods=['GET'])
def get_messages():
    try:
        current_messages = load_messages()
        return jsonify(current_messages)
    except Exception as e:
        print(f"Ошибка получения сообщений: {e}")
        return jsonify({'error': str(e)}), 500

# Отправка сообщения
@app.route('/api/messages', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        text = data.get('text')
        username = data.get('username')
        replyToId = data.get('replyToId')
        
        print(f"Отправка сообщения: {username} - {text}")
        
        if not text or not username:
            return jsonify({'error': 'Text and username are required'}), 400
        
        # Загружаем актуальные сообщения
        current_messages = load_messages()
        
        # Создаем новое сообщение
        new_message = {
            'id': len(current_messages) + 1,
            'text': text,
            'username': username,
            'timestamp': datetime.now().isoformat(),
            'replyToId': replyToId,
            'isFavorite': False,
            'editedTimestamp': None,
            'avatar': None
        }
        
        current_messages.append(new_message)
        save_messages(current_messages)
        
        # Обновляем глобальную переменную
        global messages
        messages = current_messages
        
        print(f"Сообщение отправлено. Всего сообщений: {len(current_messages)}")
        
        return jsonify({'success': True, 'message': new_message})
        
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")
        return jsonify({'error': str(e)}), 500

# Получение избранных сообщений
@app.route('/api/messages/favorites', methods=['GET'])
def get_favorite_messages():
    try:
        current_messages = load_messages()
        favorite_messages = [msg for msg in current_messages if msg.get('isFavorite')]
        return jsonify(favorite_messages)
    except Exception as e:
        print(f"Ошибка получения избранных сообщений: {e}")
        return jsonify({'error': str(e)}), 500

# Добавление/удаление из избранного
@app.route('/api/message/favorite', methods=['POST'])
def toggle_favorite():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        message_id = data.get('messageId')
        is_favorite = data.get('isFavorite')
        
        if message_id is None:
            return jsonify({'error': 'Message ID is required'}), 400
        
        # Загружаем актуальные сообщения
        current_messages = load_messages()
        
        message = next((msg for msg in current_messages if msg['id'] == message_id), None)
        if message:
            message['isFavorite'] = is_favorite
            save_messages(current_messages)
            
            # Обновляем глобальную переменную
            global messages
            messages = current_messages
            
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Message not found'}), 404
            
    except Exception as e:
        print(f"Ошибка изменения избранного: {e}")
        return jsonify({'error': str(e)}), 500

# Редактирование сообщения
@app.route('/api/message/edit', methods=['POST'])
def edit_message():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        message_id = data.get('messageId')
        new_text = data.get('newText')
        
        if not message_id or not new_text:
            return jsonify({'error': 'Message ID and new text are required'}), 400
        
        # Загружаем актуальные сообщения
        current_messages = load_messages()
        
        message = next((msg for msg in current_messages if msg['id'] == message_id), None)
        if message:
            message['text'] = new_text
            message['editedTimestamp'] = datetime.now().isoformat()
            save_messages(current_messages)
            
            # Обновляем глобальную переменную
            global messages
            messages = current_messages
            
            return jsonify({'success': True, 'editedTimestamp': message['editedTimestamp']})
        else:
            return jsonify({'error': 'Message not found'}), 404
            
    except Exception as e:
        print(f"Ошибка редактирования сообщения: {e}")
        return jsonify({'error': str(e)}), 500

# Поиск пользователей
@app.route('/api/users/search', methods=['GET'])
def search_users():
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify([])
        
        current_users = load_users()
        filtered_users = [
            {
                'id': user['id'],
                'username': user['username'],
                'avatar': user.get('avatar'),
                'aboutMe': user.get('aboutMe', ''),
                'status': user.get('status', 'online')
            }
            for user in current_users 
            if query in user['username'].lower()
        ]
        return jsonify(filtered_users)
    except Exception as e:
        print(f"Ошибка поиска пользователей: {e}")
        return jsonify({'error': str(e)}), 500

# Получение всех пользователей
@app.route('/api/users', methods=['GET'])
def get_all_users():
    try:
        current_users = load_users()
        # Возвращаем пользователей без паролей
        users_data = [
            {
                'id': user['id'],
                'username': user['username'],
                'avatar': user.get('avatar'),
                'aboutMe': user.get('aboutMe', ''),
                'status': user.get('status', 'online'),
                'created_at': user.get('created_at')
            }
            for user in current_users
        ]
        return jsonify(users_data)
    except Exception as e:
        print(f"Ошибка получения пользователей: {e}")
        return jsonify({'error': str(e)}), 500

# Приватные сообщения - получение
@app.route('/api/private-messages', methods=['GET'])
def get_private_messages():
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username parameter is required'}), 400
        
        current_private_messages = load_private_messages()
        
        # Фильтруем сообщения для этого пользователя
        user_messages = [
            msg for msg in current_private_messages 
            if msg['receiver'] == username or msg['sender'] == username
        ]
        
        return jsonify(user_messages)
    except Exception as e:
        print(f"Ошибка получения приватных сообщений: {e}")
        return jsonify({'error': str(e)}), 500

# Приватные сообщения - отправка
@app.route('/api/private-message', methods=['POST'])
def send_private_message():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        text = data.get('text')
        username = data.get('username')  # отправитель
        receiver = data.get('receiver')  # получатель
        
        if not text or not username or not receiver:
            return jsonify({'error': 'Text, username and receiver are required'}), 400
        
        # Загружаем актуальные приватные сообщения
        current_private_messages = load_private_messages()
        
        # Создаем новое приватное сообщение
        new_message = {
            'id': len(current_private_messages) + 1,
            'text': text,
            'sender': username,
            'receiver': receiver,
            'timestamp': datetime.now().isoformat(),
            'isFavorite': False,
            'editedTimestamp': None
        }
        
        current_private_messages.append(new_message)
        save_private_messages(current_private_messages)
        
        # Обновляем глобальную переменную
        global private_messages
        private_messages = current_private_messages
        
        return jsonify({'success': True, 'message': new_message})
        
    except Exception as e:
        print(f"Ошибка отправки приватного сообщения: {e}")
        return jsonify({'error': str(e)}), 500

# Обновление профиля пользователя
@app.route('/api/user/profile/update', methods=['POST'])
def update_profile():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        avatar = data.get('avatar')
        aboutMe = data.get('aboutMe')
        
        # В реальном приложении здесь должна быть аутентификация
        # и определение текущего пользователя
        
        # Для демонстрации просто возвращаем успех
        return jsonify({
            'success': True, 
            'message': 'Profile updated successfully',
            'user': {
                'avatar': avatar,
                'aboutMe': aboutMe
            }
        })
        
    except Exception as e:
        print(f"Ошибка обновления профиля: {e}")
        return jsonify({'error': str(e)}), 500

# Создание тестового пользователя
@app.route('/api/create-test-user', methods=['POST'])
def create_test_user():
    """Создает тестового пользователя для демонстрации"""
    try:
        current_users = load_users()
        
        # Удаляем старого тестового пользователя если есть
        current_users = [u for u in current_users if u['username'] != 'test']
        
        test_user = {
            'id': len(current_users) + 1,
            'username': 'test',
            'password': 'test',
            'created_at': datetime.now().isoformat(),
            'avatar': None,
            'aboutMe': 'Тестовый пользователь для демонстрации',
            'status': 'online'
        }
        
        current_users.append(test_user)
        save_users(current_users)
        
        # Обновляем глобальную переменную
        global users
        users = current_users
        
        print(f"Создан тестовый пользователь: test/test")
        
        return jsonify({
            'success': True,
            'message': 'Test user created successfully',
            'user': {
                'id': test_user['id'],
                'username': test_user['username']
            }
        })
    except Exception as e:
        print(f"Ошибка создания тестового пользователя: {e}")
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    current_users = load_users()
    current_messages = load_messages()
    current_private_messages = load_private_messages()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'users_count': len(current_users),
        'messages_count': len(current_messages),
        'private_messages_count': len(current_private_messages),
        'users': [u['username'] for u in current_users]
    })

# Информация о сервере
@app.route('/api/info', methods=['GET'])
def server_info():
    return jsonify({
        'name': 'iNOVA Messenger API',
        'version': '1.0.0',
        'endpoints': [
            '/api/register - POST - Регистрация',
            '/api/login - POST - Вход',
            '/api/messages - GET/POST - Сообщения',
            '/api/users - GET - Пользователи',
            '/api/health - GET - Статус сервера'
        ]
    })

if __name__ == '__main__':
    # Создаем файлы если их нет
    if not os.path.exists(USERS_FILE):
        save_users([])
        print("Создан файл пользователей")
    
    if not os.path.exists(MESSAGES_FILE):
        save_messages([])
        print("Создан файл сообщений")
    
    if not os.path.exists(PRIVATE_MESSAGES_FILE):
        save_private_messages([])
        print("Создан файл приватных сообщений")
    
    # Создаем тестового пользователя если нет пользователей
    current_users = load_users()
    if len(current_users) == 0:
        test_user = {
            'id': 1,
            'username': 'test',
            'password': 'test',
            'created_at': datetime.now().isoformat(),
            'avatar': None,
            'aboutMe': 'Тестовый пользователь',
            'status': 'online'
        }
        current_users.append(test_user)
        save_users(current_users)
        users = current_users
        print("Автоматически создан тестовый пользователь: test/test")
    
    port = int(os.environ.get('PORT', 5000))
    print(f"Сервер запущен на порту {port}")
    print(f"Доступные пользователи: {[u['username'] for u in users]}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
