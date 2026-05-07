import random
from flask import Flask, render_template
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "guess-number-secret"
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}
players = {}


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def on_connect():
    pass


@socketio.on("disconnect")
def on_disconnect():
    sid = request.sid
    info = players.pop(sid, None)
    if not info:
        return
    room_id = info.get("room")
    if room_id and room_id in rooms:
        room = rooms[room_id]
        room["players"] = [p for p in room["players"] if p["sid"] != sid]
        leave_room(room_id)
        emit("system_message", f"{info['nickname']} 离开了房间", room=room_id)
        if not room["players"]:
            del rooms[room_id]
        else:
            room["game_started"] = False
            room["current_turn"] = None
            emit("game_over", {"winner": None, "message": "对手已离开，等待新玩家加入..."}, room=room_id)


@socketio.on("join_lobby")
def on_join_lobby(data):
    nickname = data.get("nickname", "匿名玩家").strip()
    if not nickname:
        nickname = "匿名玩家"
    players[request.sid] = {"nickname": nickname, "room": None}
    room_list = []
    for rid, room in rooms.items():
        room_list.append({
            "id": rid,
            "name": room["name"],
            "players": len(room["players"]),
            "max_players": 2,
        })
    emit("room_list", room_list)


@socketio.on("create_room")
def on_create_room(data):
    sid = request.sid
    room_name = data.get("name", "游戏房间").strip()
    if not room_name:
        room_name = "游戏房间"
    room_id = f"room_{random.randint(1000, 9999)}"
    while room_id in rooms:
        room_id = f"room_{random.randint(1000, 9999)}"

    rooms[room_id] = {
        "name": room_name,
        "players": [{"sid": sid, "nickname": players[sid]["nickname"]}],
        "target": None,
        "current_turn": None,
        "game_started": False,
    }
    players[sid]["room"] = room_id
    join_room(room_id)
    emit("room_joined", {"room_id": room_id, "room_name": room_name})
    emit("system_message", f"{players[sid]['nickname']} 创建了房间", room=room_id)
    _broadcast_room_list()


@socketio.on("join_room")
def on_join_room(data):
    sid = request.sid
    room_id = data.get("room_id")
    if room_id not in rooms:
        emit("error_message", "房间不存在")
        return
    room = rooms[room_id]
    if len(room["players"]) >= 2:
        emit("error_message", "房间已满")
        return

    room["players"].append({"sid": sid, "nickname": players[sid]["nickname"]})
    players[sid]["room"] = room_id
    join_room(room_id)
    emit("room_joined", {"room_id": room_id, "room_name": room["name"]})
    emit("system_message", f"{players[sid]['nickname']} 加入了房间", room=room_id)
    _broadcast_room_list()

    if len(room["players"]) == 2:
        _start_game(room_id)


@socketio.on("leave_room")
def on_leave_room():
    sid = request.sid
    info = players.get(sid)
    if not info or not info["room"]:
        return
    room_id = info["room"]
    if room_id in rooms:
        room = rooms[room_id]
        room["players"] = [p for p in room["players"] if p["sid"] != sid]
        leave_room(room_id)
        emit("system_message", f"{info['nickname']} 离开了房间", room=room_id)
        room["game_started"] = False
        room["current_turn"] = None
        if not room["players"]:
            del rooms[room_id]
        else:
            remaining = room["players"][0]
            emit("game_over", {"winner": None, "message": "对手已离开，等待新玩家加入..."}, room=room_id)
    info["room"] = None
    emit("left_room")
    _broadcast_room_list()


@socketio.on("guess")
def on_guess(data):
    sid = request.sid
    info = players.get(sid)
    if not info or not info["room"]:
        return
    room_id = info["room"]
    room = rooms.get(room_id)
    if not room or not room["game_started"]:
        return
    if room["current_turn"] != sid:
        emit("error_message", "还没轮到你！")
        return

    try:
        guess = int(data.get("number", 0))
    except (ValueError, TypeError):
        emit("error_message", "请输入有效数字")
        return

    if guess < 1 or guess > 100:
        emit("error_message", "请输入 1-100 之间的数字")
        return

    target = room["target"]
    nickname = info["nickname"]

    if guess == target:
        emit("guess_result", {
            "nickname": nickname,
            "guess": guess,
            "result": "correct",
        }, room=room_id)
        emit("game_over", {
            "winner": nickname,
            "message": f"🎉 {nickname} 猜对了！答案是 {target}",
        }, room=room_id)
        room["game_started"] = False
        return

    hint = "大了" if guess > target else "小了"
    emit("guess_result", {
        "nickname": nickname,
        "guess": guess,
        "result": hint,
    }, room=room_id)

    other = [p for p in room["players"] if p["sid"] != sid]
    if other:
        room["current_turn"] = other[0]["sid"]
        emit("turn_update", {"current_turn": other[0]["nickname"]}, room=room_id)


@socketio.on("restart_game")
def on_restart():
    sid = request.sid
    info = players.get(sid)
    if not info or not info["room"]:
        return
    room_id = info["room"]
    room = rooms.get(room_id)
    if not room or len(room["players"]) != 2:
        return
    _start_game(room_id)


@socketio.on("chat_message")
def on_chat(data):
    sid = request.sid
    info = players.get(sid)
    if not info or not info["room"]:
        return
    msg = data.get("message", "").strip()
    if not msg:
        return
    emit("chat_message", {
        "nickname": info["nickname"],
        "message": msg,
    }, room=info["room"])


def _start_game(room_id):
    room = rooms[room_id]
    room["target"] = random.randint(1, 100)
    room["game_started"] = True
    first = random.choice(room["players"])
    room["current_turn"] = first["sid"]
    emit("game_start", {
        "turn": first["nickname"],
        "message": "游戏开始！{} 先猜".format(first["nickname"]),
    }, room=room_id)
    emit("turn_update", {"current_turn": first["nickname"]}, room=room_id)


def _broadcast_room_list():
    room_list = []
    for rid, room in rooms.items():
        room_list.append({
            "id": rid,
            "name": room["name"],
            "players": len(room["players"]),
            "max_players": 2,
        })
    emit("room_list", room_list)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
