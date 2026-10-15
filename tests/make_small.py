"""Build tests/q_small.json: 100 messages = the same 25 scenarios in Arabic, English, mixed and Arabizi.

Picks chats from tests/q_<lang>.json (built by make_multilang.py), covering every question type:
12 factual (fees, situation fees, time, places, documents, notes, conditions), 3 comparison,
3 wrong assumption, 2 unclear, 3 out of scope, 1 two-turn conversation.
Run: python3 tests/make_small.py
"""
import json
from pathlib import Path

# 0-based chat indices in each q_<lang>.json
FACTS = [0, 5, 8, 10, 11, 13, 17, 21, 25, 28, 33, 39]
COMPARISON = [40 + i for i in (0, 2, 5)]
WRONG = [46 + i for i in (0, 2, 4)]
UNCLEAR = [52 + i for i in (0, 3)]
OUT_OF_SCOPE = [57 + i for i in (0, 3, 5)]
CONVERSATION = [64]
PICK = FACTS + COMPARISON + WRONG + UNCLEAR + OUT_OF_SCOPE + CONVERSATION

if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    chats = []
    for lang in ("ar", "en", "mx", "az"):
        src = json.loads((here / f"q_{lang}.json").read_text(encoding="utf-8"))["chats"]
        picked = [src[i] for i in PICK]
        assert sum(len(c["messages"]) for c in picked) == 25, lang
        chats += picked
    (here / "q_small.json").write_text(json.dumps({"chats": chats}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"q_small.json: {sum(len(c['messages']) for c in chats)} messages")
