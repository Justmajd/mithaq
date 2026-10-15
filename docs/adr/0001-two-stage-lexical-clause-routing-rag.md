# 0001 — Two-Stage Lexical & Clause Routing Over Naive Vector Chunking
2026-10-15 · Status: accepted

## Context
The system is built for the 42 Irbid AI Hackathon to answer citizen queries regarding 12 official Civil Status and Passports Department services in Jordan. The knowledge base consists of 12 small, highly structured legal documents (approx. 15-20 pages total) sharing ~85% vocabulary overlap across fees, required documents, eligibility rules, and office procedures.

Traditional Naive Vector Chunking (e.g. splitting into 500-token chunks with embedding cosine similarity) presented severe failure modes:
1. **Severe Cross-Service Collisions**: Services like "Passport First Issue" vs. "Passport Renewal" share identical keywords, causing naive vector embeddings to retrieve the wrong service.
2. **Table & Condition Splitting**: Arbitrary chunk boundaries slice fee tables away from their age conditions (under 16 vs. 16+), leading to arithmetic hallucinations.
3. **Context Dumping Penalties**: The hackathon rules strictly penalize dumping whole files or irrelevant context blocks into `contexts`.
4. **Time & Offline Constraints**: The hackathon is 4 hours with no guaranteed internet connectivity for downloading heavy vector databases.

## Decision
We implemented a deterministic **Two-Stage Lexical & Clause Routing Engine** with targeted canonical section extractors:
1. **Clause Splitting & Normalization**: Splits complex multi-service queries along linguistic boundaries (`و`, `أو`, `أم`, `ولا`, `مقابل`, `and`, `or`, `vs`) and handles attached prepositions (`للـ`, `بالـ`, `والـ`), Arabic root normalization, and Arabizi transliteration.
2. **Canonical Section Extractor**: Extracts only the precise section required by the query (`الرسوم`, `الوثائق المطلوبة`, `شروط تقديم الخدمة`, `أماكن تقديم الخدمة`, `الزمن المستغرق`) formatted strictly as:  
   `"{Service Title} - {Section Header}: {Snippet}"`.
3. **Local LLM Grounding**: Passes exact snippets to local Ollama (`command-r7b-arabic:7b`) with temperature 0.1, strict grounding rules, and time conversion hints.
4. **Guardrails & Fallback**: Integrates prompt injection shielding, numerical fact-checking, and a deterministic offline fallback ensuring zero runtime crashes.

## Consequences
- **Positive**: 100% routing accuracy across 300 test questions (Fusha, Ammiya, English).
- **Positive**: Zero context dumping penalties; all citations strictly match required canonical schema.
- **Positive**: Extremely fast execution (~14s for official dataset, <2s for 300-question validator).
- **Positive**: 100% offline self-containment with zero external network calls.
- **Negative / Trade-off**: Adding an entirely new domain outside Civil Status requires defining its service schema and section headers in `SERVICE_FILES`.
