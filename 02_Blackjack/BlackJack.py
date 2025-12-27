import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


# -----------------------------
# カードと点数計算
# -----------------------------
def make_deck(shuffle: bool = True) -> List[str]:
    """52枚デッキを作る（スートは省略してランクのみ）"""
    ranks = ["A"] + [str(n) for n in range(2, 11)] + ["J", "Q", "K"]
    deck = []
    for _ in range(4):  # 4スート分
        deck.extend(ranks)
    if shuffle:
        random.shuffle(deck)
    return deck


def hand_value(hand: List[str]) -> int:
    """
    手牌の合計点を計算する。
    Aは最初11で数え、21を超えたら1に落とす。
    """
    total = 0
    aces = 0

    for card in hand:
        if card == "A":
            total += 11
            aces += 1
        elif card in ("J", "Q", "K"):
            total += 10
        else:
            total += int(card)

    # 21を超える限りA(11)をA(1)に落とす（= -10）
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    return total


def is_blackjack(hand: List[str]) -> bool:
    """2枚で21ならブラックジャック"""
    return len(hand) == 2 and hand_value(hand) == 21


# -----------------------------
# ゲーム状態
# -----------------------------
@dataclass
class BlackjackState:
    deck: List[str] = field(default_factory=list)
    player_hand: List[str] = field(default_factory=list)
    dealer_hand: List[str] = field(default_factory=list)
    phase: str = "not_started"  # not_started / player_turn / dealer_turn / finished
    result: Optional[str] = None  # player_win / dealer_win / push / None


# -----------------------------
# 外部から使うAPI
# -----------------------------
state = BlackjackState()


def new_game() -> Dict[str, Any]:
    """
    新しいゲーム開始：
    プレイヤー2枚、ディーラー2枚配る（ディーラーの1枚は隠し）
    """
    global state
    if not state.deck:
        state.deck = make_deck()

    state.player_hand = []
    state.dealer_hand = []
    state.phase = "player_turn"
    state.result = None

    if len(state.deck) < 4:
        state.deck = make_deck()

    # 初期配牌
    state.player_hand = [state.deck.pop(), state.deck.pop()]
    state.dealer_hand = [state.deck.pop(), state.deck.pop()]

    # 初手ブラックジャック判定（簡易ルール）
    p_bj = is_blackjack(state.player_hand)
    d_bj = is_blackjack(state.dealer_hand)

    if p_bj or d_bj:
        state.phase = "finished"
        if p_bj and d_bj:
            state.result = "push"
        elif p_bj:
            state.result = "player_win"
        else:
            state.result = "dealer_win"

        return _build_response(status="finished", message="初手で決着しました。")

    return _build_response(status="started", message="ゲーム開始！ Hit か Stand を選んでください。")


def player_hit() -> Dict[str, Any]:
    """プレイヤーが1枚引く"""
    if state.phase != "player_turn":
        return {"status": "error", "message": "今はHitできません。ゲームを開始してください。"}

    state.player_hand.append(state.deck.pop())
    p_value = hand_value(state.player_hand)

    if p_value > 21:
        state.phase = "finished"
        state.result = "dealer_win"
        return _build_response(status="bust", message="バーストしました（21超え）。負けです。")

    if p_value == 21:
        # 21に到達したら自動Stand（簡易）
        return player_stand()

    return _build_response(status="player_turn", message="Hitしました。続けますか？")


def player_stand() -> Dict[str, Any]:
    """プレイヤーが止まる → ディーラーターンへ"""
    if state.phase != "player_turn":
        return {"status": "error", "message": "今はStandできません。ゲームを開始してください。"}

    state.phase = "dealer_turn"
    return dealer_play()


def dealer_play() -> Dict[str, Any]:
    """ディーラーが17以上になるまで引く → 勝敗判定"""
    if state.phase != "dealer_turn":
        return {"status": "error", "message": "ディーラーのターンではありません。"}

    while hand_value(state.dealer_hand) < 17:
        state.dealer_hand.append(state.deck.pop())

    state.phase = "finished"
    return _judge_and_finish()


def reveal() -> Dict[str, Any]:
    """現在の状態を返す（UI表示用）"""
    if state.phase == "not_started":
        return {"status": "error", "message": "ゲームを開始してください。"}
    return _build_response(status="state", message="現在の状態です。")


def give_up() -> Dict[str, Any]:
    """ギブアップ（即負け）"""
    if state.phase == "not_started":
        return {"status": "error", "message": "ゲームを開始してください。"}

    state.phase = "finished"
    state.result = "dealer_win"
    return _build_response(status="giveup", message="ギブアップしました。負けです。")


# -----------------------------
# 内部ユーティリティ
# -----------------------------
def _judge_and_finish() -> Dict[str, Any]:
    p = hand_value(state.player_hand)
    d = hand_value(state.dealer_hand)

    if d > 21:
        state.result = "player_win"
        return _build_response(status="finished", message="ディーラーがバースト！勝ちです。")

    if p > d:
        state.result = "player_win"
        return _build_response(status="finished", message="あなたの勝ちです。")
    if p < d:
        state.result = "dealer_win"
        return _build_response(status="finished", message="ディーラーの勝ちです。")

    state.result = "push"
    return _build_response(status="finished", message="引き分けです。")


def _build_response(status: str, message: str) -> Dict[str, Any]:
    """
    UI側が使いやすいように、毎回同じ形で返す。
    ディーラー手札は、プレイヤーターン中は1枚隠す。
    """
    p_hand = list(state.player_hand)
    d_hand = list(state.dealer_hand)

    if state.phase == "player_turn":
        # ディーラーの2枚目を隠す
        d_visible = [d_hand[0], "?"]
        d_value = None
    else:
        d_visible = d_hand
        d_value = hand_value(d_hand)

    return {
        "status": status,
        "phase": state.phase,
        "message": message,
        "player": {
            "hand": p_hand,
            "value": hand_value(p_hand),
            "blackjack": is_blackjack(p_hand),
        },
        "dealer": {
            "hand": d_visible,
            "value": d_value,
            "blackjack": is_blackjack(d_hand) if state.phase != "player_turn" else None,
        },
        "result": state.result,
        "deck_remaining": len(state.deck),
    }
