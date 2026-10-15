"""
Government Services RAG System for 42 Irbid AI Hackathon
Optimized for:
1. High-precision service and section routing (Handling colloquial Jordanian dialect, MSA, and comparisons)
2. Exact context extraction matching the evaluation format: "{Service} - {Section}: {Snippet}"
3. Multi-turn chat context memory across sequential messages
4. Out-of-scope refusal detection
5. Fast, robust Ollama integration (command-r7b-arabic:7b) with offline safety fallbacks
"""

import os
import sys
import json
import re
import requests
from typing import List, Dict, Any, Tuple, Optional

# Ensure standard UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")

OLLAMA_API_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "command-r7b-arabic:7b"

# 12 Core Services Definitions
SERVICE_FILES = {
    "passport_first_issue": {
        "file": "passport_first_issue.txt",
        "doc_type": "passport",
        "action": "first_issue",
        "title": "جواز سفر لأول مرة",
        "aliases": [
            "جواز سفر لاول مرة", "جواز سفر اول مرة", "جواز السفر لاول مرة", "جواز السفر اول مرة",
            "جواز سفر عادي لاول مرة", "جواز سفر جديد", "باسبور اول مرة", "اول جواز سفر"
        ]
    },
    "passport_renewal": {
        "file": "passport_renewal.txt",
        "doc_type": "passport",
        "action": "renewal",
        "title": "تجديد جواز السفر",
        "aliases": [
            "تجديد جواز السفر", "تجديد جواز سفر", "تجديد جواز", "تجديد باسبور", "تجديد الجواز",
            "باسبور منتهي", "جواز منتهي", "انتهى جوازي", "بدي اجدد جوازي", "اجدد جوازي"
        ]
    },
    "passport_lost": {
        "file": "passport_lost.txt",
        "doc_type": "passport",
        "action": "lost",
        "title": "جواز سفر بدل فاقد",
        "aliases": [
            "جواز سفر بدل فاقد", "جواز بدل فاقد", "باسبور بدل فاقد", "فقدان جواز", "ضاع جوازي",
            "فقدت جوازي", "ضيعت باسبوري", "باسبور ضاع"
        ]
    },
    "passport_damaged": {
        "file": "passport_damaged.txt",
        "doc_type": "passport",
        "action": "damaged",
        "title": "جواز سفر بدل تالف",
        "aliases": [
            "جواز سفر بدل تالف", "جواز بدل تالف", "باسبور بدل تالف", "تلف جواز", "جواز تالف",
            "باسبور تالف", "اهترى جوازي", "باسبور مهتري"
        ]
    },
    "id_card_first_issue": {
        "file": "id_card_first_issue.txt",
        "doc_type": "id_card",
        "action": "first_issue",
        "title": "إصدار البطاقة الذكية لأول مرة",
        "aliases": [
            "البطاقة الذكية لاول مرة", "البطاقة الذكية اول مرة", "بطاقة ذكية لاول مرة", "بطاقة ذكية اول مرة",
            "اصدار البطاقة الذكية", "اصدار هوية", "هوية لاول مرة", "اول هوية", "صار عمري 16", "صار عمري 18"
        ]
    },
    "id_card_renewal": {
        "file": "id_card_renewal.txt",
        "doc_type": "id_card",
        "action": "renewal",
        "title": "تجديد البطاقة الذكية",
        "aliases": [
            "تجديد البطاقة الذكية", "تجديد بطاقة الاحوال", "تجديد الهوية", "هوية منتهية",
            "بطاقة منتهية", "اجدد هويتي", "تجديد البطاقة"
        ]
    },
    "id_card_lost": {
        "file": "id_card_lost.txt",
        "doc_type": "id_card",
        "action": "lost",
        "title": "بطاقة ذكية بدل فاقد",
        "aliases": [
            "بطاقة ذكية بدل فاقد", "البطاقة الذكية بدل فاقد", "هوية بدل فاقد", "ضاعت هويتي",
            "فقدت الهوية", "هوية ضايعة", "فقدان البطاقة الذكية"
        ]
    },
    "id_card_damaged": {
        "file": "id_card_damaged.txt",
        "doc_type": "id_card",
        "action": "damaged",
        "title": "بطاقة ذكية بدل تالف",
        "aliases": [
            "بطاقة ذكية بدل تالف", "البطاقة الذكية بدل تالف", "هوية بدل تالف", "هوية مكسورة",
            "هوية تالفة", "هوية مهترية", "تلف البطاقة الذكية"
        ]
    },
    "family_book_first_issue": {
        "file": "family_book_first_issue.txt",
        "doc_type": "family_book",
        "action": "first_issue",
        "title": "إصدار دفتر العائلة لأول مرة",
        "aliases": [
            "دفتر عائلة لاول مرة", "دفتر العائلة لاول مرة", "دفتر عائلة اول مرة", "دفتر العائلة اول مرة",
            "اصدار دفتر عائلة", "اصدار دفتر العائلة", "دفتر عائلة جديد", "دفتر عيلة اول مرة", "تزوجت وبدي دفتر عائلة"
        ]
    },
    "family_book_renewal": {
        "file": "family_book_renewal.txt",
        "doc_type": "family_book",
        "action": "renewal",
        "title": "تجديد دفتر العائلة",
        "aliases": [
            "تجديد دفتر العائلة", "تجديد دفتر عائلة", "تجديد دفتر عيلة", "دفتر العائلة مليان", "تجديد الدفتر"
        ]
    },
    "family_book_lost": {
        "file": "family_book_lost.txt",
        "doc_type": "family_book",
        "action": "lost",
        "title": "دفتر عائلة بدل فاقد",
        "aliases": [
            "دفتر عائلة بدل فاقد", "دفتر العائلة بدل فاقد", "دفتر عيلة بدل فاقد", "ضاع دفتر العائلة", "فقدان دفتر العائلة"
        ]
    },
    "family_book_damaged": {
        "file": "family_book_damaged.txt",
        "doc_type": "family_book",
        "action": "damaged",
        "title": "دفتر عائلة بدل تالف",
        "aliases": [
            "دفتر عائلة بدل تالف", "دفتر العائلة بدل تالف", "دفتر عيلة بدل تالف", "دفتر العائلة مهتري", "تلف دفتر العائلة"
        ]
    }
}

# Standard Out of Scope topics that must be politely declined
OUT_OF_SCOPE_KEYWORDS = [
    "طيران", "تذكر", "سياح", "فندق", "دبي", "قطر", "مطار",
    "شهاده جامعي", "جامع", "تعليم عالي", "توجيهي", "معادله شهاد", "تصديق شهاد", "مدرس",
    "رخصه قياد", "رخصه سير", "سواق", "مخالفات", "نقل ملكي", "ترخيص سيار", "مركب",
    "ضريبه", "مسقفات", "بلدي", "كهرباء", "مياه", "ضمان اجتماعي", "تقاعد",
    "طقس", "مباراه", "مطعم", "منسف", "عاصم"
]


OUT_OF_SCOPE_RESPONSE = (
    "عذراً، لا تتوفر لدي معلومات عن هذا الموضوع. "
    "أستطيع المساعدة في خدمات جواز السفر ودفتر العائلة والبطاقة الذكية فقط."
)

UNCLEAR_RESPONSE = (
    "يرجى تحديد الوثيقة أو الخدمة المطلوبة (جواز السفر، أو البطاقة الذكية، أو دفتر العائلة) لنتمكن من تزويدك بالتفاصيل بدقة."
)


class ServiceKB:
    """Manages the 12 documents and section parsing."""
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.services_data: Dict[str, Dict[str, Any]] = {}
        self._load_and_parse()

    def _load_and_parse(self):
        for s_key, s_meta in SERVICE_FILES.items():
            fpath = os.path.join(self.data_dir, s_meta["file"])
            if not os.path.exists(fpath):
                continue
            raw_text = open(fpath, encoding="utf-8").read()
            sections = self._parse_sections(raw_text)
            self.services_data[s_key] = {
                "meta": s_meta,
                "raw": raw_text,
                "sections": sections
            }

    def _parse_sections(self, text: str) -> Dict[str, str]:
        canonical_headers = [
            "الفئة المستفيدة",
            "أماكن تقديم الخدمة",
            "شروط تقديم الخدمة",
            "الوثائق المطلوبة للحصول على الخدمة",
            "إجراءات تقديم الخدمة",
            "الزمن المستغرق لتقديم الخدمة",
            "شركاء الخدمة",
            "ملاحظات",
            "الرسوم"
        ]
        sections = {}
        lines = text.splitlines()
        current_header = None
        current_content = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            matched_header = None
            for h in canonical_headers:
                if line_str.startswith(h):
                    matched_header = h
                    break
            
            if matched_header:
                if current_header:
                    sections[current_header] = "\n".join(current_content).strip()
                current_header = matched_header
                # Remainder of the line after header
                remainder = line_str[len(matched_header):].strip()
                if remainder.startswith("\t"):
                    remainder = remainder.lstrip("\t ")
                current_content = [remainder] if remainder else []
            else:
                if current_header:
                    current_content.append(line_str)
                else:
                    # Headerless top lines (menus/titles)
                    pass

        if current_header and current_content:
            sections[current_header] = "\n".join(current_content).strip()

        return sections


def normalize_arabic(text: str) -> str:
    """Clean and normalize Arabic text for robust keyword and pattern matching."""
    t = text.lower()
    t = re.sub(r"[إأآا]", "ا", t)
    t = re.sub(r"ة", "ه", t)
    t = re.sub(r"ى", "ي", t)
    t = re.sub(r"[ًٌٍَُِّْ]", "", t)  # strip tashkeel
    # Normalize attached prefixes: 'لل' -> 'ال', 'بال' -> 'ال', 'وال' -> 'ال'
    t = re.sub(r"\bلل", "ال", t)
    t = re.sub(r"\bبال", "ال", t)
    t = re.sub(r"\bوال", "ال", t)
    t = re.sub(r"\bلتجديد", "تجديد", t)
    t = re.sub(r"\bلاول", "اول", t)
    return t


def is_out_of_scope(question: str, prior_services: Optional[List[str]] = None) -> bool:
    norm_q = normalize_arabic(question)
    for kw in OUT_OF_SCOPE_KEYWORDS:
        if normalize_arabic(kw) in norm_q:
            return True
    
    # If there is prior service context in this conversation, it is in-scope
    if prior_services:
        return False

    # Check if question has any government document domain keywords
    doc_keywords = [
        "جواز", "باسبور", "سفر", "عائل", "عيل", "دفتر", "بطاق", "هوي", "احوال", "ذكيه",
        "صوره", "رسوم", "وثائق", "شروط", "اجراءات", "رب الاسره", "غرامة", "كفالة", "زمرة الدم",
        "سفار", "قنصل", "مكتب", "خدمة", "تجديد", "اجدد", "جدد", "فاقد", "تالف", "اصدار", "اطلع", "مستعجل",
        "مطلوب", "اوراق", "تزوج", "زواج"
    ]
    has_domain_word = any(normalize_arabic(w) in norm_q for w in doc_keywords)
    if not has_domain_word and len(question.strip().split()) > 2:
        return True
    return False


def is_unclear_question(question: str, prior_services: Optional[List[str]] = None) -> bool:
    """Detects if user is asking an ambiguous question without specifying the document."""
    if prior_services:
        return False
    norm_q = normalize_arabic(question)
    
    has_doc_type = any(k in norm_q for k in [
        "جواز", "باسبور", "سفر", "دفتر", "عائل", "عيل", "بطاق", "هوي", "احوال", "ذكيه", "رب الاسره"
    ])
    if has_doc_type:
        return False
        
    intent_keywords = [
        "اجدد", "تجديد", "منتهي", "خلص",
        "فاقد", "ضاع", "ضاعت", "ضيعت", "فقدان",
        "تالف", "مهتري", "اهتري", "مكسور", "خربان",
        "اصدار", "اطلع", "استخراج", "اعمل", "اول مره",
        "اوراق", "وثائق", "مطلوب", "يلزم", "بحتاج",
        "رسوم", "سعر", "تكلف", "تكلفة", "بدفع", "كم بكلف",
        "وين بقدم", "وين اروح", "اماكن", "وقت", "زمن", "يستغرق", "قديش بدها"
    ]
    return any(k in norm_q for k in intent_keywords)


def detect_services(question: str, prior_services: List[str] = None) -> List[str]:
    """Identifies which of the 12 services the question refers to."""
    norm_q = normalize_arabic(question)
    found_services = []

    # 1. First, check if exact aliases match anywhere
    for s_key, s_meta in SERVICE_FILES.items():
        for alias in s_meta["aliases"]:
            if normalize_arabic(alias) in norm_q:
                if s_key not in found_services:
                    found_services.append(s_key)

    has_comparison = any(k in norm_q for k in ["ايهما", "ايها", "الفرق", "مقارنه", " ولا ", " ام "])
    if found_services and not has_comparison:
        return found_services

    # Pre-extract any global doc types in the question
    global_docs = []
    if any(k in norm_q for k in ["جواز", "باسبور"]):
        global_docs.append("passport")
    if any(k in norm_q for k in ["دفتر عائل", "دفتر عيل", "العائل", "رب الاسره", "تزوج", "زواج", "عقد زواج"]):
        global_docs.append("family_book")
    if any(k in norm_q for k in ["بطاق", "هوي", "احوال مدني", "ذكيه", "زمرة الدم"]):
        global_docs.append("id_card")

    # 2. Check by clauses to associate doc_type with action correctly (avoids Cartesian explosion)
    clauses = re.split(r"[،,\n]|(?:\s+(?:و|أو|أم|ولا|مقابل|بينما)\s+)", question)
    
    last_doc = None
    for clause in clauses:
        c_norm = normalize_arabic(clause)
        c_docs = []
        if any(k in c_norm for k in ["جواز", "باسبور"]):
            c_docs.append("passport")
        if any(k in c_norm for k in ["دفتر عائل", "دفتر عيل", "العائل", "رب الاسره", "تزوج", "زواج", "عقد زواج"]):
            c_docs.append("family_book")
        if any(k in c_norm for k in ["بطاق", "هوي", "احوال مدني", "ذكيه", "زمرة الدم"]):
            c_docs.append("id_card")

        if c_docs:
            last_doc = c_docs[0]
        elif last_doc:
            c_docs = [last_doc]
        elif len(global_docs) == 1:
            c_docs = list(global_docs)

        c_actions = []
        if any(k in c_norm for k in ["فاقد", "ضاع", "فقدت", "فقدان", "ضايع"]):
            c_actions.append("lost")
        if any(k in c_norm for k in ["تالف", "مهتري", "اهتري", "تلف", "مكسور", "خربان"]):
            c_actions.append("damaged")
        if any(k in c_norm for k in ["تجديد", "اجدد", "منتهي", "خلص", "باقي عليه", "مستعجل"]):
            c_actions.append("renewal")
        
        has_first = (
            any(k in c_norm for k in ["اول مره", "اول هويه", "صار عمري", "تزوج", "زواج", "عقد زواج", "ما طلعت"]) or
            ("جديد" in c_norm and "تجديد" not in c_norm and "التجديد" not in c_norm)
        )
        has_generic = any(k in c_norm for k in ["اصدار", "اطلع", "استخراج", "اعمل"])
        if "فاقد" in c_norm:
            pass  # 'اول مرة' modifies lost, not first_issue
        elif has_first or (has_generic and not c_actions):
            c_actions.append("first_issue")

        if c_docs and c_actions:
            for d in c_docs:
                for a in c_actions:
                    k = f"{d}_{a}"
                    if k in SERVICE_FILES and k not in found_services:
                        found_services.append(k)

    if found_services:
        return found_services

    # 3. Whole-question fallback
    doc_types = list(global_docs)
    actions = []
    if any(k in norm_q for k in ["فاقد", "ضاع", "فقدت", "فقدان", "ضايع"]):
        actions.append("lost")
    if any(k in norm_q for k in ["تالف", "مهتري", "اهتري", "تلف", "مكسور", "خربان"]):
        actions.append("damaged")
    if any(k in norm_q for k in ["تجديد", "اجدد", "منتهي", "خلص", "باقي عليه", "مستعجل"]):
        actions.append("renewal")
    
    has_first = (
        any(k in norm_q for k in ["اول مره", "اول هويه", "صار عمري", "تزوج", "زواج", "عقد زواج", "ما طلعت"]) or
        ("جديد" in norm_q and "تجديد" not in norm_q and "التجديد" not in norm_q)
    )
    has_generic = any(k in norm_q for k in ["اصدار", "اطلع", "استخراج", "اعمل"])
    if "فاقد" in norm_q:
        pass
    elif has_first or (has_generic and not actions):
        actions.append("first_issue")

    if doc_types and actions:
        for d in doc_types:
            for a in actions:
                k = f"{d}_{a}"
                if k in SERVICE_FILES and k not in found_services:
                    found_services.append(k)

    # 4. If doc_types exist but no action, default to renewal or first issue based on words
    if not found_services and doc_types:
        for d in doc_types:
            found_services.append(f"{d}_renewal")


    # 5. Handle follow-up context (Multi-turn conversational bonus!)
    if not found_services and prior_services:
        found_services = list(prior_services)

    return found_services



def detect_target_sections(question: str) -> List[str]:
    """Determines which sections of the service file contain the answer."""
    norm_q = normalize_arabic(question)
    sections = []

    # Time / Duration
    if any(k in norm_q for k in ["وقت", "زمن", "يستغرق", "قديش بدها", "مده", "ساعه", "دقيق"]):
        sections.append("الزمن المستغرق لتقديم الخدمة")

    # Location / Places
    if any(k in norm_q for k in ["وين", "مكان", "اماكن", "سفار", "قنصلي", "مكتب", "مكاتب", "خارج", "برا البلد"]):
        sections.append("أماكن تقديم الخدمة")

    # Documents / Requirements / Photos
    if any(k in norm_q for k in ["اوراق", "وثائق", "مطلوب", "يلزم", "بحتاج", "صور", "صوره شخصي"]):
        sections.append("الوثائق المطلوبة للحصول على الخدمة")

    # Fees / Cost
    if any(k in norm_q for k in ["رسوم", "سعر", "تكلف", "تكلفة", "بدفع", "دينار", "قديش بكلف"]):
        sections.append("الرسوم")
        sections.append("ملاحظات")

    # Conditions / Age / Rules
    if any(k in norm_q for k in ["شروط", "شرط", "عمر", "سنه", "قاصر", "زوجه", "زوجها", "موافق", "رب الاسره", "توفي"]):
        sections.append("شروط تقديم الخدمة")
        sections.append("ملاحظات")

    # Procedure / Steps
    if any(k in norm_q for k in ["اجراءات", "خطوات", "دور", "وصل", "شباك", "طريقه"]):
        sections.append("إجراءات تقديم الخدمة")

    if not sections:
        # If question is broad, include the most common fact sections
        sections = ["الوثائق المطلوبة للحصول على الخدمة", "الرسوم", "شروط تقديم الخدمة", "ملاحظات"]

    return sections


def build_contexts(kb: ServiceKB, service_keys: List[str], target_sections: List[str], question: str) -> List[str]:
    """
    Builds context snippets strictly matching the evaluation requirement:
    "{Service Title} - {Section Header}: {Snippet}"
    """
    contexts = []
    norm_q = normalize_arabic(question)

    for s_key in service_keys:
        s_data = kb.services_data.get(s_key)
        if not s_data:
            continue
        title = s_data["meta"]["title"]
        s_sections = s_data["sections"]

        for sec_name in target_sections:
            content = s_sections.get(sec_name, "")
            if not content:
                # Try partial match on section name
                for k, v in s_sections.items():
                    if sec_name in k or k in sec_name:
                        sec_name = k
                        content = v
                        break
            if not content:
                continue

            # If user asks specifically about photo count ("صور شخصية"), extract that line if present
            if "صور" in norm_q or "صوره" in norm_q:
                photo_lines = [
                    l.strip() for l in content.splitlines() 
                    if any(p in l for p in ["صور شخصية", "صورة شخصية", "صور ملونة", "صورة ملونة", "حديثة وملونة"])
                ]
                if photo_lines:
                    snippet = f"{title} - الوثائق المطلوبة: ... " + " ".join(photo_lines)
                    contexts.append(snippet)
                    continue

            # Clean and format snippet
            clean_content = " ".join(content.split())
            
            # Map canonical header for nice display
            header_label = sec_name
            if "الوثائق" in sec_name:
                header_label = "الوثائق المطلوبة"
            elif "الزمن" in sec_name:
                header_label = "الزمن المستغرق لتقديم الخدمة"
            elif "أماكن" in sec_name:
                header_label = "أماكن تقديم الخدمة"
            elif "شروط" in sec_name:
                header_label = "شروط تقديم الخدمة"
            elif "الرسوم" in sec_name:
                header_label = "الرسوم"
            elif "ملاحظات" in sec_name:
                header_label = "ملاحظات"
            elif "إجراءات" in sec_name:
                header_label = "إجراءات تقديم الخدمة"
            
            entry = f"{title} - {header_label}: {clean_content}"
            if entry not in contexts:
                contexts.append(entry)

    return contexts


def generate_answer_via_ollama(question: str, contexts: List[str], model: str = DEFAULT_MODEL) -> str:
    """Calls Ollama locally to generate an accurate, grounded Arabic answer."""
    if not contexts:
        return OUT_OF_SCOPE_RESPONSE

    context_block = "\n".join(f"- {c}" for c in contexts)
    system_prompt = (
        "أنت مساعد رسمي موثوق لخدمات دائرة الأحوال المدنية والجوازات الأردنية.\n"
        "مهمتك: الإجابة على سؤال المواطن فقط وبدقة تامة اعتماداً على السياق الرسمي المرفق أدناه.\n"
        "تعليمات صارمة:\n"
        "1. اعتمد حصراً على المعلومات المذكورة في السياق.\n"
        "2. انقل الأرقام، المدد، المبالغ، والوثائق المطلوبة بدقة تامة دون زيادة أو اختراع.\n"
        "3. أجب بشكل مباشر وموجز ومحدد دون مقدمات ودون عبارات ختامية مثل 'هل هناك استفسار آخر'.\n"
        "4. إذا تضمن السؤال افتراضاً خاطئاً (مثل اشتراط موافقة الزوج)، صحح الافتراض استناداً للسياق.\n"
        "5. إذا كان السؤال مقارنة بين خدمات، اذكر قيمة الرسم لكل خدمة من السياق ثم وضح أيهما أعلى أو أقل وفقاً للأرقام.\n"
        "6. انتبه لحساب المدد الزمنية بدقة: (الشهر = 30 يوماً، 3 شهور = 90 يوماً، 4 شهور = 120 يوماً وهي أكثر من 90 يوماً، 6 شهور = 180 يوماً)."
    )

    user_prompt = f"السياق الرسمي:\n{context_block}\n\nسؤال المواطن: {question}\nالجواب المباشر:"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,  # Low temperature to avoid hallucination
            "num_predict": 256
        }
    }

    try:
        resp = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        if resp.status_code == 200:
            result = resp.json()
            answer = result.get("message", {}).get("content", "").strip()
            if answer:
                return answer
    except Exception as e:
        sys.stderr.write(f"Ollama call warning: {e}\n")

    # Safe deterministic fallback if Ollama model is busy or cold
    return build_deterministic_fallback(question, contexts)


def build_deterministic_fallback(question: str, contexts: List[str]) -> str:
    """Fast, reliable fallback that extracts facts from context if Ollama is unreachable."""
    if not contexts:
        return OUT_OF_SCOPE_RESPONSE
    # Synthesize from contexts
    c_text = " ".join(contexts)
    # Check for duration
    if "45 دقيقة" in c_text and ("يستغرق" in question or "وقت" in question):
        return "يستغرق تقديم هذه الخدمة 45 دقيقة."
    # Check for places
    if "أماكن تقديم الخدمة" in c_text and ("وين" in question or "مكان" in question):
        return "يمكنك تقديم الطلب في مكاتب دائرة الأحوال المدنية والجوازات، أو في السفارات والقنصليات الأردنية في الخارج."
    # Generic grounded return
    clean_parts = [c.split(":", 1)[-1].strip() for c in contexts if ":" in c]
    return "بناءً على التعليمات الرسمية: " + "؛ ".join(clean_parts[:2])


def process_questions(questions_path: str, output_path: str, data_dir: str, model: str = DEFAULT_MODEL):
    """Processes the questions file and produces the scored answers.json file."""
    print(f"Loading data from: {data_dir}")
    kb = ServiceKB(data_dir)

    print(f"Reading questions from: {questions_path}")
    with open(questions_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    chats = data.get("chats", [])
    output_chats = []

    for chat in chats:
        chat_id = chat.get("chat_id")
        messages = chat.get("messages", [])
        prior_services = []
        processed_messages = []

        for msg in messages:
            msg_id = msg.get("message_id")
            question = msg.get("question", "").strip()

            try:
                # 1. Out of Scope Check
                if is_out_of_scope(question, prior_services=prior_services):
                    ans = OUT_OF_SCOPE_RESPONSE
                    ctx = []
                elif is_unclear_question(question, prior_services=prior_services):
                    ans = UNCLEAR_RESPONSE
                    ctx = []
                else:
                    # 2. Service Routing
                    service_keys = detect_services(question, prior_services=prior_services)
                    if service_keys:
                        prior_services = service_keys  # update memory for multi-turn

                    # 3. Section Extraction
                    target_sections = detect_target_sections(question)

                    # 4. Build Contexts
                    ctx = build_contexts(kb, service_keys, target_sections, question)

                    # 5. LLM Answer Generation
                    ans = generate_answer_via_ollama(question, ctx, model=model)

            except Exception as e:
                # Brief requirement: Never crash, produce error fallback
                sys.stderr.write(f"Error on message {msg_id}: {e}\n")
                ans = "عذراً، حدث خطأ أثناء معالجة السؤال."
                ctx = []

            processed_messages.append({
                "message_id": msg_id,
                "question": question,
                "answer": ans,
                "contexts": ctx
            })

        output_chats.append({
            "chat_id": chat_id,
            "messages": processed_messages
        })

    result_payload = {"chats": output_chats}

    print(f"Writing answers to: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, ensure_ascii=False, indent=2)

    print(f"Successfully processed {len(output_chats)} chats!")


if __name__ == "__main__":
    q_file = sys.argv[1] if len(sys.argv) > 1 else "questions.json"
    curr_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
    
    # Locate data directory
    if os.path.exists(os.path.join(curr_dir, "data")):
        d_dir = os.path.join(curr_dir, "data")
    elif os.path.exists("data"):
        d_dir = "data"
    elif os.path.exists("participant_pack/data"):
        d_dir = "participant_pack/data"
    else:
        d_dir = "data"

    out_file = os.path.join(os.path.dirname(q_file) or ".", "answers.json")
    process_questions(q_file, out_file, d_dir, model=DEFAULT_MODEL)
