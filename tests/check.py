"""Score answers.json against a test file with "must" / "ctx" expectations.

Usage: python3 tests/check.py tests/questions_more.json answers.json

- must: list of groups; every group needs at least one of its strings in the answer
        (compared after Arabic normalisation, so أ/ا, ة/ه, tashkeel don't matter).
- ctx:  "empty" -> contexts must be []; or a list of service names -> every listed service
        must appear in contexts and no context may come from another service.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from main import norm  # noqa: E402


def check(exp, got):
    problems = []
    answer, contexts = got.get("answer", ""), got.get("contexts", [])
    if answer == "error":
        return ["answer is error"]
    na = norm(answer)
    for group in exp.get("must", []):
        if not any(norm(s) in na for s in group):
            problems.append(f"missing one of {group}")
    for bad in exp.get("must_not", []):
        if norm(bad) in na:
            problems.append(f"contains forbidden {bad!r}")
    ctx = exp.get("ctx")
    if ctx == "empty" and contexts:
        problems.append(f"expected no contexts, got {len(contexts)}")
    elif isinstance(ctx, list):
        sources = {c.split(" - ", 1)[0] for c in contexts}
        for name in ctx:
            if name not in sources:
                problems.append(f"no context from {name}")
        extra = sources - set(ctx)
        if extra:
            problems.append(f"wrong source {sorted(extra)}")
    return problems


def main():
    qfile, afile = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "answers.json"
    expected = {m["message_id"]: m for c in json.load(open(qfile, encoding="utf-8"))["chats"] for m in c["messages"]}
    answers = {m["message_id"]: m for c in json.load(open(afile, encoding="utf-8"))["chats"]
               for m in c.get("messages", []) if isinstance(m, dict) and "message_id" in m}
    by_type = defaultdict(lambda: [0, 0])
    by_lang = defaultdict(lambda: [0, 0])
    for mid, exp in expected.items():
        got = answers.get(mid)
        problems = ["no answer in file"] if got is None else check(exp, got)
        lang = mid.split("-")[0] if mid.split("-")[0] in ("ar", "en", "mx", "az") else None
        by_type[exp.get("type", "?")][1] += 1
        if lang:
            by_lang[lang][1] += 1
        if problems:
            print(f"FAIL {mid} [{exp.get('type')}] {exp['question']}")
            print(f"     answer: {(got or {}).get('answer', '')[:200]}")
            for p in problems:
                print(f"     - {p}")
        else:
            by_type[exp.get("type", "?")][0] += 1
            if lang:
                by_lang[lang][0] += 1
    print("\nby type:")
    for t, (ok, n) in sorted(by_type.items()):
        print(f"  {t:18s} {ok}/{n}")
    if by_lang:
        names = {"ar": "Arabic", "en": "English", "mx": "Arabic/English", "az": "Arabizi"}
        print("\nby language:")
        for l in ("ar", "en", "mx", "az"):
            if l in by_lang:
                print(f"  {names[l]:18s} {by_lang[l][0]}/{by_lang[l][1]}")
    ok = sum(v[0] for v in by_type.values())
    n = sum(v[1] for v in by_type.values())
    print(f"\nTOTAL {ok}/{n} passed")


if __name__ == "__main__":
    main()
