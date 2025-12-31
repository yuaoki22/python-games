from BlackJack import (
    new_game,
    player_hit,
    player_stand,
    reveal,
    set_bet,
)


def _available_commands(state: dict) -> list:
    phase = state.get("phase")
    chips = state.get("chips")
    bet = state.get("bet")

    if phase == "player_turn":
        return ["hit", "stand", "reveal", "end"]
    if phase == "dealer_turn":
        return ["reveal", "end"]
    if phase == "finished":
        if chips and chips > 0:
            return ["bet", "new", "reveal", "end"]
        return ["reveal", "end"]

    if chips and chips > 0:
        if bet and bet > 0:
            return ["new", "reveal", "end"]
        return ["bet", "reveal", "end"]
    return ["reveal", "end"]


def main():
    last_res = new_game()
    print(last_res)

    while True:
        commands = _available_commands(last_res)
        cmd = input(f"{'/'.join(commands)} > ").strip().lower()
        if not cmd:
            print({"status": "error", "message": f"choose from: {'/'.join(commands)}"})
            continue

        action = cmd.split()[0]
        if action not in commands:
            print({"status": "error", "message": f"choose from: {'/'.join(commands)}"})
            continue

        if action == "hit":
            res = player_hit()
        elif action == "stand":
            res = player_stand()
        elif action == "reveal":
            res = reveal()
        elif action == "new":
            res = new_game()
        elif action == "bet":
            parts = cmd.split()
            if len(parts) == 1:
                res = set_bet(100)
            elif len(parts) == 2 and parts[1].isdigit():
                res = set_bet(int(parts[1]))
            else:
                print({"status": "error", "message": "use: bet or bet 100"})
                continue
        elif action == "end":
            print({"status": "end", "message": "game end"})
            break
        else:
            print({"status": "error", "message": f"choose from: {'/'.join(commands)}"})
            continue

        print(res)
        last_res = res


if __name__ == "__main__":
    main()
