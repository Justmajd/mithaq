# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-15

### Added
- **Two-Stage Lexical & Clause Routing Engine**: Maps questions with high precision across 12 civil status services (Passports, Smart ID, Family Book).
- **Exact Section Extractor**: Produces canonical evaluation snippets formatted as `"{Service Title} - {Section Header}: {Snippet}"`.
- **Arabizi / Franco-Arabic Transliteration**: Real-time phonetic and token transliteration for Latin-based Jordanian Arabic (e.g. `baddi a6ale3 jawaz 2awwal marra`).
- **Comprehensive Guardrails**:
  - `Input Guard`: Detects jailbreak, prompt injection, and system override attempts.
  - `Domain Boundary Guard`: Rejects off-topic inquiries (driving licenses, university degrees, taxes, flights) with `contexts: []`.
  - `Ambiguity Guard`: Detects under-specified action queries and requests clarification with `contexts: []`.
  - `Output Fact & Numerical Guard`: Verifies that fee amounts mentioned in answers exist in context snippets to prevent numerical hallucinations.
  - `Output Sanitizer`: Strips trailing chatbot pleasantries and filler text.
- **Multilingual Support**: Supports Modern Standard Arabic (Fusha), Jordanian Colloquial Dialect (Ammiya), English, and Arabizi.
- **Multi-Turn Chat Context Memory**: Resolves sequential messages within a conversation to the previously discussed service while resetting between chats.
- **Benchmark Suite**: 300 test questions (`test_100_fusha.json`, `test_100_ammiya.json`, `test_100_english.json`, and `test_300_master.json`).
- **Lightning Offline Validator**: `fast_validate_300.py` verifying routing and grounding in under 2 seconds.

### Fixed
- Fixed Cartesian product explosion when multiple document types and actions appear in conjunction clauses.
- Fixed substring collision between `جديد` (new/first issue) and `تجديد` (renewal).
- Fixed attached preposition prefixes (`للـ`, `بالـ`, `والـ`, `لتجديد`, `لاول`).
- Fixed marriage late penalty arithmetic for 7B models by injecting unit conversion guidance (4 months = 120 days > 90 days legal grace period).
