from BlackJack import (
    new_game,
    player_hit,
    player_stand,
    reveal,
    give_up,
)


def main():
    print(new_game())

    while True:
        cmd = input("hit/stand/reveal/new/end > ").strip().lower()

        if cmd == "hit":
            res = player_hit()
        elif cmd == "stand":
            res = player_stand()
        elif cmd == "reveal":
            res = reveal()
        elif cmd == "new":
            res = new_game()
        elif cmd == "end":
            print({"status": "end", "message": "ゲームを終了します"})
            break
        else:
            print({"status": "error", "message": "hit/stand/reveal/new/end から選んでください"})
            continue

        print(res)

        if res.get("phase") == "finished":
            break

if __name__ == "__main__":
    main()
