from flask import Flask, request, jsonify, send_file
import random, threading, time, json, os

app = Flask(__name__)

# 数据文件
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'rooms': {}, 'banned': [], 'users': {}, 'pid_counter': 100}

def save_data(d):
    with open(DATA_FILE, 'w') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

data = load_data()
rooms = data.get('rooms', {})
banned = data.get('banned', [])
users = data.get('users', {})
pid_counter = data.get('pid_counter', 100)
lock = threading.Lock()

@app.route('/')
def home():
    return jsonify({'status': 'ok', 'service': 'survival-code-multiplayer'})

# ============ 游戏 API ============

@app.route('/create', methods=['POST'])
def create_room():
    global pid_counter
    d = request.json or {}
    name = d.get('name', 'player')
    
    if name in banned:
        return jsonify({'ok': False, 'err': '你已被封禁'})
    
    with lock:
        pid = str(pid_counter)
        pid_counter += 1
        room_code = str(random.randint(100000, 999999))
        while room_code in rooms:
            room_code = str(random.randint(100000, 999999))
        rooms[room_code] = {
            'players': {pid: {'name': name, 'ready': False, 'x': 0, 'y': 0}},
            'host': pid,
            'created': time.time()
        }
        users[name] = {'last_online': time.time(), 'room': room_code}
        data['rooms'] = rooms
        data['users'] = users
        data['pid_counter'] = pid_counter
        save_data(data)
    
    return jsonify({'ok': True, 'room': room_code, 'pid': pid})

@app.route('/join', methods=['POST'])
def join_room():
    global pid_counter
    d = request.json or {}
    room_code = d.get('room', '')
    name = d.get('name', 'player')
    
    if name in banned:
        return jsonify({'ok': False, 'err': '你已被封禁'})
    
    with lock:
        if room_code not in rooms:
            return jsonify({'ok': False, 'err': '房间不存在'})
        if len(rooms[room_code]['players']) >= 2:
            return jsonify({'ok': False, 'err': '房间已满'})
        
        pid = str(pid_counter)
        pid_counter += 1
        rooms[room_code]['players'][pid] = {'name': name, 'ready': False, 'x': 0, 'y': 0}
        users[name] = {'last_online': time.time(), 'room': room_code}
        data['rooms'] = rooms
        data['users'] = users
        data['pid_counter'] = pid_counter
        save_data(data)
    
    return jsonify({'ok': True, 'room': room_code, 'pid': pid})

@app.route('/sync', methods=['POST'])
def sync():
    d = request.json or {}
    room_code = d.get('room', '')
    pid = d.get('pid', '')
    
    with lock:
        if room_code not in rooms or pid not in rooms[room_code]['players']:
            return jsonify({'ok': False, 'err': '不在房间'})
        
        rooms[room_code]['players'][pid]['ready'] = d.get('ready', False)
        rooms[room_code]['players'][pid]['x'] = d.get('x', 0)
        rooms[room_code]['players'][pid]['y'] = d.get('y', 0)
        players = rooms[room_code]['players']
        data['rooms'] = rooms
        save_data(data)
    
    return jsonify({'ok': True, 'players': players})

@app.route('/leave', methods=['POST'])
def leave():
    d = request.json or {}
    room_code = d.get('room', '')
    pid = d.get('pid', '')
    
    with lock:
        if room_code in rooms and pid in rooms[room_code]['players']:
            del rooms[room_code]['players'][pid]
            if not rooms[room_code]['players']:
                del rooms[room_code]
        data['rooms'] = rooms
        save_data(data)
    
    return jsonify({'ok': True})

# ============ 管理后台 API ============

@app.route('/admin')
def admin_page():
    return send_file('admin.html')

@app.route('/admin/api/stats')
def admin_stats():
    with lock:
        online = sum(len(r['players']) for r in rooms.values())
        return jsonify({
            'online_players': online,
            'total_users': len(users),
            'active_rooms': len(rooms),
            'banned_count': len(banned),
            'banned_list': banned
        })

@app.route('/admin/api/users')
def admin_users():
    with lock:
        user_list = []
        for name, info in users.items():
            user_list.append({
                'name': name,
                'last_online': info.get('last_online', 0),
                'room': info.get('room', ''),
                'banned': name in banned
            })
        user_list.sort(key=lambda x: -x['last_online'])
        return jsonify(user_list)

@app.route('/admin/api/ban', methods=['POST'])
def admin_ban():
    d = request.json or {}
    name = d.get('name', '')
    if name and name not in banned:
        banned.append(name)
        data['banned'] = banned
        save_data(data)
    return jsonify({'ok': True})

@app.route('/admin/api/unban', methods=['POST'])
def admin_unban():
    d = request.json or {}
    name = d.get('name', '')
    if name in banned:
        banned.remove(name)
        data['banned'] = banned
        save_data(data)
    return jsonify({'ok': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
