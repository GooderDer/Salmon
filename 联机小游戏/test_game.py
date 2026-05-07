import socketio
import time
import sys

sio = socketio.Client()
sio2 = socketio.Client()

results = {"player1_events": [], "player2_events": []}


@sio.on("connect")
def p1_connect():
    results["player1_events"].append("connected")


@sio.on("room_list")
def p1_room_list(data):
    results["player1_events"].append(("room_list", len(data)))


@sio.on("room_joined")
def p1_room_joined(data):
    results["player1_events"].append(("room_joined", data))


@sio.on("system_message")
def p1_system(msg):
    results["player1_events"].append(("system", msg))


@sio.on("game_start")
def p1_game_start(data):
    results["player1_events"].append(("game_start", data))


@sio.on("turn_update")
def p1_turn(data):
    results["player1_events"].append(("turn", data))


@sio.on("guess_result")
def p1_guess_result(data):
    results["player1_events"].append(("guess_result", data))


@sio.on("game_over")
def p1_game_over(data):
    results["player1_events"].append(("game_over", data))


@sio.on("chat_message")
def p1_chat(data):
    results["player1_events"].append(("chat", data))


# Player 2
@sio2.on("connect")
def p2_connect():
    results["player2_events"].append("connected")


@sio2.on("room_list")
def p2_room_list(data):
    results["player2_events"].append(("room_list", len(data)))


@sio2.on("room_joined")
def p2_room_joined(data):
    results["player2_events"].append(("room_joined", data))


@sio2.on("system_message")
def p2_system(msg):
    results["player2_events"].append(("system", msg))


@sio2.on("game_start")
def p2_game_start(data):
    results["player2_events"].append(("game_start", data))


@sio2.on("turn_update")
def p2_turn(data):
    results["player2_events"].append(("turn", data))


@sio2.on("guess_result")
def p2_guess_result(data):
    results["player2_events"].append(("guess_result", data))


@sio2.on("game_over")
def p2_game_over(data):
    results["player2_events"].append(("game_over", data))


@sio2.on("chat_message")
def p2_chat(data):
    results["player2_events"].append(("chat", data))


def main():
    print("=== 测试 1: 连接服务器 ===")
    sio.connect("http://localhost:5000")
    sio2.connect("http://localhost:5000")
    time.sleep(0.5)
    assert "connected" in results["player1_events"], "Player 1 连接失败"
    assert "connected" in results["player2_events"], "Player 2 连接失败"
    print("  [PASS] 两个玩家都连接成功")

    print("=== 测试 2: 进入大厅 ===")
    sio.emit("join_lobby", {"nickname": "玩家A"})
    sio2.emit("join_lobby", {"nickname": "玩家B"})
    time.sleep(0.5)
    p1_rooms = [e for e in results["player1_events"] if isinstance(e, tuple) and e[0] == "room_list"]
    assert len(p1_rooms) > 0, "Player 1 未收到房间列表"
    print("  [PASS] 大厅房间列表获取成功")

    print("=== 测试 3: 创建房间 ===")
    sio.emit("create_room", {"name": "测试房间"})
    time.sleep(0.5)
    p1_joined = [e for e in results["player1_events"] if isinstance(e, tuple) and e[0] == "room_joined"]
    assert len(p1_joined) > 0, "Player 1 未收到 room_joined"
    room_id = p1_joined[-1][1]["room_id"]
    print(f"  [PASS] 房间创建成功, room_id={room_id}")

    print("=== 测试 4: 加入房间 & 游戏开始 ===")
    sio2.emit("join_room", {"room_id": room_id})
    time.sleep(0.5)
    p2_joined = [e for e in results["player2_events"] if isinstance(e, tuple) and e[0] == "room_joined"]
    assert len(p2_joined) > 0, "Player 2 未加入房间"
    p1_gs = [e for e in results["player1_events"] if isinstance(e, tuple) and e[0] == "game_start"]
    p2_gs = [e for e in results["player2_events"] if isinstance(e, tuple) and e[0] == "game_start"]
    assert len(p1_gs) > 0, "Player 1 未收到 game_start"
    assert len(p2_gs) > 0, "Player 2 未收到 game_start"
    print("  [PASS] 双方都收到了游戏开始事件")

    print("=== 测试 5: 聊天功能 ===")
    sio.emit("chat_message", {"message": "你好，准备好了吗？"})
    time.sleep(0.3)
    p2_chat_events = [e for e in results["player2_events"] if isinstance(e, tuple) and e[0] == "chat"]
    assert len(p2_chat_events) > 0, "Player 2 未收到聊天消息"
    assert p2_chat_events[-1][1]["message"] == "你好，准备好了吗？"
    assert p2_chat_events[-1][1]["nickname"] == "玩家A"
    print("  [PASS] 聊天消息收发正常")

    print("=== 测试 6: 猜数字 ===")
    # Determine who goes first
    p1_turns = [e for e in results["player1_events"] if isinstance(e, tuple) and e[0] == "turn"]
    p2_turns = [e for e in results["player2_events"] if isinstance(e, tuple) and e[0] == "turn"]
    assert p1_turns or p2_turns, "没有人获得回合"
    first_turn = p1_turns[-1][1]["current_turn"] if p1_turns else p2_turns[-1][1]["current_turn"]

    if first_turn == "玩家A":
        guesser, other, other_events = sio, sio2, results["player2_events"]
        guesser_name = "玩家A"
    else:
        guesser, other, other_events = sio2, sio, results["player1_events"]
        guesser_name = "玩家B"

    guesser.emit("guess", {"number": 50})
    time.sleep(0.3)
    gr = [e for e in other_events if isinstance(e, tuple) and e[0] == "guess_result"]
    assert len(gr) > 0, "对手未收到猜数字结果"
    result = gr[-1][1]["result"]
    assert result in ("大了", "小了", "correct"), f"未知结果: {result}"
    print(f"  [PASS] {guesser_name} 猜了 50, 结果: {result}")

    # Clean up
    sio.disconnect()
    sio2.disconnect()
    print("\n=== 全部测试通过 ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[FAIL] {e}")
        sio.disconnect()
        sio2.disconnect()
        sys.exit(1)
