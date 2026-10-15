# Project Guidelines: Jordan Civil Status & Passports RAG (42 Irbid AI Hackathon)

## Stack & Architecture
- **Language**: Python 3.10+
- **Inference Runtime**: Ollama running locally (`command-r7b-arabic:7b` at `http://127.0.0.1:11434/api/chat`)
- **Knowledge Base**: 12 structured text documents in `data/` across Passports, Smart ID Card, and Family Book
- **Architecture**: Two-stage intent & clause-scoped routing + canonical section extractor + Guardrails + deterministic offline fallback

## Commands
```bash
# Official evaluation execution (generates answers.json)
python main.py questions.json

# Fast offline validation across all 300 test questions (Fusha, Ammiya, English) in ~1s
python fast_validate_300.py

# Run specific edge cases suite
python main.py test_edge_cases.json

# Run Arabizi and Guardrails jailbreak verification suite
python main.py test_arabizi_guardrails.json

# Syntax check
python -m py_compile main.py
```

## Non-Negotiable Rules
1. **Offline Only**: The system must run completely detached from the internet. All inference goes through local Ollama or deterministic fallback.
2. **Context Format**: Contexts MUST strictly follow: `"{Service Title} - {Section Header}: {Snippet}"`.
3. **Never Dump Whole Files**: Always extract targeted section snippets to avoid context dumping penalties.
4. **Out of Scope & Ambiguity**:
   - Out of scope queries (driving, taxes, university degrees, flights) -> polite refusal + `contexts: []`.
   - Ambiguous queries without document specified -> clarification prompt + `contexts: []`.
5. **Languages Supported**: Modern Standard Arabic (Fusha), Jordanian Dialect (Ammiya), English, and Arabizi / Franco-Arabic.
