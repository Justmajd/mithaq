# Mithaq — Jordan civil-status services chatbot

Answers citizens' questions about **passports, family books and smart ID cards** using only the 12 documents in `data/`.
Every answer is generated at runtime by the provided model **`command-r7b-arabic:7b`** (Ollama). **`bge-m3`** runs locally for embeddings.

## Run

```bash
ollama pull command-r7b-arabic:7b
ollama pull bge-m3
python main.py questions.json        # or: python3 main.py questions.json
```

- Writes `answers.json` next to `main.py`, in the same structure as the input, with `answer` and `contexts` added to every message.
- Needs only the Python standard library (3.8+): no `pip install`.
- Works fully offline once the two models are pulled. Ollama must be running on `localhost:11434`.
- Takes about 4–5 seconds per question on an M1 Pro.

## Project layout

| Path | What it is |
|---|---|
| `main.py` | The whole bot: data loading, routing, retrieval, prompting, guardrails, output |
| `data/` | The 12 service documents (unchanged) |
| `questions.json` / `answers.json` | Practice input and the bot's output for it |
| `tests/` | Test sets, generators and the scorer (`check.py`) |

## How it works

**1. Data handling**
- Each file is cleaned: menu leftovers like الرئيسية / الخدمات / شارك are dropped.
- Each file is split into its 9 fields: الفئة المستفيدة، أماكن تقديم الخدمة، الشروط، الوثائق المطلوبة، الإجراءات، الزمن المستغرق، شركاء الخدمة، ملاحظات، الرسوم.
- Every field becomes a chunk `"<service> - <field>: <text>"`.
- Notes are split into one chunk per rule, because facts hide there.
- Wording is never changed.

**2. Finding the right information.** This step is deterministic, so look-alike files are never confused.
- Keywords pick the **document** (passport / family book / ID card) and the **situation** (first time / renewal / lost / damaged).
  This works in Arabic (MSA and Jordanian dialect), English, mixed Arabic/English and Arabizi (e.g. `da3at hawiyti`, `tajdeed el jawaz`).
- A question that names two services (a comparison) gets both. A follow-up message reuses the service from earlier in the same chat.
- Field keywords pick the section (fees, documents, time, places, conditions…). Generic words like "how much", "kam" and "who" count only
  when nothing more specific matches. Deadline words ("خلال", "within", "5ilal") point to the notes. `bge-m3` similarity is the fallback
  when no keyword matches.
- **Fee-case selector:** fees depend on the asker's case. The bot reads the case from the question (age, expired or still valid, abroad or
  in Jordan, military, full pages, first or later loss, late fine) and keeps only the fee lines that apply.

**3. Answering without making things up**
- The selected chunks go to the model in Command-R's native grounded-RAG format, as search-tool results.
- Notes are listed first, or the fee lines first for fee questions. Each fee line is its own document.
- On comparisons, the model is told to answer for every service named.
- The system prompt tells the model to:
  - answer only from the results, and copy numbers exactly;
  - pick the case that matches the asker;
  - treat a rule in the notes as overriding general information (e.g. when the document is handed over);
  - correct false assumptions;
  - otherwise say the information is not available.
- **Number check:** if an answer contains a number found in neither the documents nor the question, it is regenerated. Number words in the
  documents (e.g. السادسة عشر = 16, أسبوعين = 2 weeks) count as found.
- `contexts` lists only the chunks used: note items the answer doesn't reflect are dropped.

**4. Guardrails.** All of these return `contexts: []`.
- Off-topic questions (flights, visas, licences…) are declined.
- Unclear questions ("قديش الرسوم؟") get a clarifying question.
- Illegal requests (forgery, bribery) and requests for other people's personal data are refused.
- Questions about other countries' passports, and services not in the data, are declined.
- Prompt-injection attempts are ignored.

**5. Robustness**
- Each message is wrapped in try/except, so a failure gives `"answer": "error"` instead of a crash.
- `answers.json` is saved after every chat, and malformed input is skipped.
- Ollama calls retry once.
- English questions get English answers. Arabic, mixed and Arabizi questions are answered in Arabic.

## Tests

```bash
python3 tests/make_multilang.py     # builds 4 × 70 questions: Arabic, English, mixed, Arabizi
python3 tests/make_small.py         # builds the 100-question subset (25 per language, all question types)
python3 main.py tests/q_small.json && python3 tests/check.py tests/q_small.json answers.json
```

`tests/check.py` checks each answer for three things:
- the key fact (`must`);
- content that must not appear (`must_not`);
- the right source (`ctx`).

The facts behind the expected answers are in `tests/FACTS.md`. Running a test set overwrites `answers.json`. Run `python main.py questions.json` again afterwards.

| Test set | Result |
|---|---|
| 100 questions (25 each: Arabic, English, mixed, Arabizi) | 84/100 on the last full run (23 / 22 / 20 / 19). Then 13 of the 16 failures were fixed (verified on those 16). Full set not re-run since |
| Guardrails (`tests/q_guard.json`: injection, illegal requests, personal data, other countries, garbage, long input) | 26/26 (run before the last fixes) |
| Practice `questions.json` | 6/6 answered from the right service, with no errors |

## Known issues

- A false claim phrased as a check ("takes two days صح؟") sometimes gets "not available" instead of the correction.
- Some Arabizi questions about rules in the notes still miss the rule: intentional passport damage → investigation committee, and the
  family book renewal deadline of 3 months.
- A question about something the documents don't cover but which sounds related (e.g. a passport delivery fee) can get an invented
  amount. The number check can't catch it when that number appears elsewhere in the documents.
