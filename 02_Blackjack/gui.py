import tkinter as tk
from tkinter import messagebox

# あなたのロジックファイル名に合わせて変更
# 例：blackjack.py にロジックがあるなら↓
from BlackJack import new_game, player_hit, player_stand, reveal, give_up


class BlackjackGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Blackjack")
        self.last_phase = None

        # 表示エリア
        self.status_label = tk.Label(root, text="Start を押してください", font=("Meiryo", 12))
        self.status_label.pack(pady=8)

        self.player_label = tk.Label(root, text="Player: ", font=("Meiryo", 12))
        self.player_label.pack(pady=4)

        self.dealer_label = tk.Label(root, text="Dealer: ", font=("Meiryo", 12))
        self.dealer_label.pack(pady=4)

        self.msg_label = tk.Label(root, text="", font=("Meiryo", 11))
        self.msg_label.pack(pady=8)

        # ボタン
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="Start", width=10, command=self.on_start)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.hit_btn = tk.Button(btn_frame, text="Hit", width=10, command=self.on_hit, state="disabled")
        self.hit_btn.grid(row=0, column=1, padx=5)

        self.stand_btn = tk.Button(btn_frame, text="Stand", width=10, command=self.on_stand, state="disabled")
        self.stand_btn.grid(row=0, column=2, padx=5)

        self.giveup_btn = tk.Button(btn_frame, text="Give up", width=10, command=self.on_giveup, state="disabled")
        self.giveup_btn.grid(row=0, column=3, padx=5)

        self.refresh_btn = tk.Button(btn_frame, text="Reveal", width=10, command=self.on_reveal)
        self.refresh_btn.grid(row=0, column=4, padx=5)

        # 初期表示
        self.update_view(reveal_safe=True)

    def set_buttons_for_phase(self, phase: str):
        # phase に応じてボタンの有効/無効を切替
        if phase in ("player_turn",):
            self.hit_btn.config(state="normal")
            self.stand_btn.config(state="normal")
            self.giveup_btn.config(state="normal")
        else:
            self.hit_btn.config(state="disabled")
            self.stand_btn.config(state="disabled")
            self.giveup_btn.config(state="disabled")

    def update_view(self, res=None, reveal_safe=False):
        # ????????????E???E??
        if res is None:
            if reveal_safe:
                res = reveal()
            else:
                res = {"status": "state", "phase": "not_started", "message": "Start ????????"}

        if res.get("status") == "error":
            phase = res.get("phase", "not_started")
            msg = res.get("message", "")
            self.status_label.config(text=f"Phase: {phase}")
            self.msg_label.config(text=msg)
            self.player_label.config(text="Player: ")
            self.dealer_label.config(text="Dealer: ")
            self.set_buttons_for_phase(phase)
            self.last_phase = phase
            return

        phase = res.get("phase", "not_started")
        msg = res.get("message", "")

        self.status_label.config(text=f"Phase: {phase}")
        self.msg_label.config(text=msg)

        player = res.get("player", {})
        dealer = res.get("dealer", {})

        p_hand = player.get("hand", [])
        p_value = player.get("value", "")
        self.player_label.config(text=f"Player: {p_hand}  (value={p_value})")

        d_hand = dealer.get("hand", [])
        d_value = dealer.get("value", None)
        if d_value is None:
            self.dealer_label.config(text=f"Dealer: {d_hand}")
        else:
            self.dealer_label.config(text=f"Dealer: {d_hand}  (value={d_value})")

        # ??E?????
        if phase == "finished" and self.last_phase != "finished":
            result = res.get("result", "")
            if result:
                messagebox.showinfo("Result", f"Result: {result}\n{msg}")

        self.set_buttons_for_phase(phase)
        self.last_phase = phase

    def on_start(self):
        res = new_game()
        self.update_view(res)

    def on_hit(self):
        res = player_hit()
        self.update_view(res)

    def on_stand(self):
        res = player_stand()
        self.update_view(res)

    def on_giveup(self):
        res = give_up()
        self.update_view(res)

    def on_reveal(self):
        res = reveal()
        self.update_view(res)


if __name__ == "__main__":
    root = tk.Tk()
    app = BlackjackGUI(root)
    root.mainloop()
