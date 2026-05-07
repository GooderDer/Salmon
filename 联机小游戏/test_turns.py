import socketio
import time
import sys

sio = socketio.Client()
sio2 = socketio.Client()
results = {"p1": [], "p2": []}

for player, key in [(sio, "p1"), (sio2, "p2")]:
    @player.on("room_joined")
    def h(data, k=key): results[k].append(("joined", data))
    @player.on("game_start")
    def h(data, k=key): results[k].append(("start", data))
    @player.on("turn_update")
    def h(data, k=key): results[k].append(("turn", data))
    @player.on("guess_result")
    def h(data, k=key): results[k].append(("result", data))
    @player.on("game_over")
    def h(data, k=key): results[k].append(("over", data))

def wait_for(events, key, tag, timeout=3):
    deadline = time.time() + timeout
    while time.time() < deadline:
        for e in events[key]:
            if isinstance(e, tuple) and e[0] == tag:
                return e
        time.sleep(0.1)
    return None

def main():
    sio.connect("http://localhost:5000")
    sio2.connect("http://localhost:5000")
    time.sleep(0.3)

    sio.emit("join_lobby", {"nickname": "A"})
    sio2.emit("join_lobby", {"nickname": "B"})
    time.sleep(0.3)

    sio.emit("create_room", {"name": "test"})
    time.sleep(0.3)
    room = [e for e in results["p1"] if isinstance(e, tuple) and e[0] == "joined"][-1][1]["room_id"]

    sio2.emit("join_room", {"room_id": room})
    time.sleep(0.5)

    # Wait for initial turn_update
    tu1 = wait_for(results, "p1", "turn")
    tu2 = wait_for(results, "p2", "turn")
    assert tu1 and tu2, "Initial turn_update not received"
    first_turn = tu1[1]["current_turn"]
    print(f"First turn: {first_turn}")

    if first_turn == "A":
        current, other, cur_key, oth_key = sio, sio2, "p1", "p2"
        cur_name, oth_name = "A", "B"
    else:
        current, other, cur_key, oth_key = sio2, sio, "p2", "p1"
        cur_name, oth_name = "B", "A"

    for i in range(3):
        print(f"\n--- Round {i+1} ---")
        # Record current turn_update counts
        before = len([e for e in results[oth_key] if isinstance(e, tuple) and e[0] == "turn"])

        current.emit("guess", {"number": 50})
        time.sleep(0.5)

        # Check guess_result received by other
        res = wait_for(results, oth_key, "result")
        assert res, f"Round {i+1}: {oth_name} didn't receive guess_result"
        print(f"  {cur_name} guessed 50 -> {res[1]['result']}")

        # Check new turn_update received by other
        after = [e for e in results[oth_key] if isinstance(e, tuple) and e[0] == "turn"]
        assert len(after) > before, f"Round {i+1}: {oth_name} didn't receive turn_update"
        new_turn = after[-1][1]["current_turn"]
        assert new_turn == oth_name, f"Round {i+1}: turn should be {oth_name}, got {new_turn}"
        print(f"  Turn switched to {oth_name} (confirmed by turn_update)")

        # Swap
        current, other = other, current
        cur_key, oth_key = oth_key, cur_key
        cur_name, oth_name = oth_name, cur_name

    print("\n=== Multi-round turn switching PASSED ===")
    sio.disconnect()
    sio2.disconnect()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[FAIL] {e}")
        sio.disconnect()
        sio2.disconnect()
        sys.exit(1)
