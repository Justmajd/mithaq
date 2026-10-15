# Mithaq — Jordan civil-status services chatbot

Answers citizens' questions about **passports, family books and smart ID cards** using only the 12 documents in `data/`.
Answers are generated at runtime by the provided model **`command-r7b-arabic:7b`** (Ollama); **`bge-m3`** is used locally for embeddings.

## Run

```bash
ollama pull command-r7b-arabic:7b
ollama pull bge-m3
python main.py questions.json        # or: python3 main.py questions.json
```

Writes `answers.json` next to `main.py`. Standard library only — no `pip install`, works fully offline once the two models are pulled. Python 3.8+.

## How it works

**1. Data handling** — each file is cleaned (menu leftovers like الرئيسية / الخدمات / شارك dropped) and split into its 9 fields
(الفئة المستفيدة, أماكن تقديم الخدمة, الشروط, الوثائق المطلوبة, الإجراءات, الزمن المستغرق, شركاء الخدمة, ملاحظات, الرسوم).
Every field becomes a chunk `"<service> - <field>: <text>"`. Notes are split into one chunk per rule, because facts hide there. Wording is never changed.

**2. Finding the right service** (deterministic, so look-alike files are never confused)
- Keyword routing picks the **document** (passport / family book / ID card) and the **situation** (first time / renewal / lost / damaged) in
  Arabic (MSA + Jordanian dialect), English, mixed Arabic/English and Arabizi (`da3at hawiyti`, `tajdeed el jawaz`).
- Questions naming two services (comparisons) get both; follow-up messages inherit the service from the same chat.
- Field keywords pick the section (fees, documents, time, places, conditions…); `bge-m3` similarity is the fallback when no keyword matches.

**3. Answering without making things up**
- The selected chunks are passed to the model in Command-R's native grounded-RAG format (as search-tool results). Notes come first
  (or fee lines first for fee questions), and each fee line is its own document, so the model picks the line that matches the asker.
- System prompt: answer only from the results, copy numbers exactly, pick the case that matches the asker, correct false assumptions,
  say "not available" otherwise.
- **Number check:** if an answer contains a number that appears in neither the documents nor the question, it is regenerated.
- `contexts` = only the chunks used (note items the answer doesn't reflect are dropped).

**4. Guardrails** — off-topic questions (flights, visas, licences…) are declined; unclear questions ("قديش الرسوم؟") get a clarifying question;
illegal requests (forgery, bribery) and requests for other people's personal data are refused; other countries' passports and services
not in the data are declined. All of these return `contexts: []`. Prompt-injection attempts are ignored.

**5. Robustness** — each message is wrapped in try/except (`"answer": "error"` on failure), `answers.json` is saved after every chat,
malformed input is skipped, Ollama calls retry once. English questions get English answers; everything else is answered in Arabic.

## Tests

```bash
python3 tests/make_multilang.py     # 4 × 70 questions: Arabic, English, mixed, Arabizi
python3 tests/make_small.py         # 100-question subset (25 per language, all question types)
python3 main.py tests/q_small.json && python3 tests/check.py tests/q_small.json answers.json
```

`tests/check.py` scores each answer for the key fact (`must`), forbidden content (`must_not`) and the right source (`ctx`).
Facts used for expectations are in `tests/FACTS.md`.

| Test set | Result |
|---|---|
| 100 questions (25 Arabic / 25 English / 25 mixed / 25 Arabizi) | 84/100 on the full run; afterwards 13 of the 16 failures fixed (fee-case selector, notes handling) — ~97/100 expected, full set not re-run |
| Guardrails (`tests/q_guard.json`: injection, illegal, personal data, other countries, garbage, long input) | 26/26 |
| Out of scope / unclear / conversation / places / time / documents | 100% on the 100-question set |

Known weak spots: rules hidden in the notes (e.g. lost ID card issued only 2 weeks after the police report) and picking the right
fee line when several cases apply.
