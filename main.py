#!/usr/bin/env python3
"""Offline Arabic RAG chatbot for Jordanian civil-status services (passport, family book, smart ID).

Keyword routing, bge-m3 embeddings as a retrieval fallback, command-r7b-arabic via a local Ollama.
Usage: python3 main.py [questions.json]   (writes answers.json next to this file)
"""
import json
import math
import os
import re
import socket
import sys
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLLAMA = "http://localhost:11434"
MODEL = os.environ.get("MITHAQ_MODEL", "command-r7b-arabic:7b")
EMBED_MODEL = os.environ.get("MITHAQ_EMBED", "bge-m3")
GROUNDED = os.environ.get("MITHAQ_GROUNDED", "1") == "1"  # use Command-R tool-result RAG format
SEARCH_TOOL = {"type": "function", "function": {
    "name": "search_services", "description": "يبحث في وثائق خدمات جواز السفر ودفتر العائلة والبطاقة الذكية",
    "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}}
OPTIONS = {"temperature": 0, "num_ctx": 8192, "num_predict": 400, "top_p": 1, "seed": 42}

# data file stem ("<doc_type>_<situation>") -> canonical service name
SERVICES = {
    "passport_first_issue": "جواز سفر لأول مرة",
    "passport_renewal": "تجديد جواز السفر",
    "passport_lost": "جواز سفر بدل فاقد",
    "passport_damaged": "جواز سفر بدل تالف",
    "family_book_first_issue": "دفتر عائلة لأول مرة",
    "family_book_renewal": "تجديد دفتر العائلة",
    "family_book_lost": "دفتر عائلة بدل فاقد",
    "family_book_damaged": "دفتر عائلة بدل تالف",
    "id_card_first_issue": "البطاقة الذكية لأول مرة",
    "id_card_renewal": "تجديد البطاقة الذكية",
    "id_card_lost": "البطاقة الذكية بدل فاقد",
    "id_card_damaged": "البطاقة الذكية بدل تالف",
}
DOC_NAMES = {"passport": "جواز السفر", "family_book": "دفتر العائلة", "id_card": "البطاقة الذكية"}
SITUATIONS = ["first_issue", "renewal", "lost", "damaged"]
HEADERS = {  # field key -> header label that starts a line in the data files
    "target": "الفئة المستفيدة",
    "places": "أماكن تقديم الخدمة",
    "conditions": "شروط تقديم الخدمة",
    "documents": "الوثائق المطلوبة للحصول على الخدمة",
    "procedure": "إجراءات تقديم الخدمة",
    "time": "الزمن المستغرق لتقديم الخدمة",
    "partners": "شركاء الخدمة",
    "notes": "ملاحظات",
    "fees": "الرسوم",
}
FIELD_ORDER = ["target", "places", "conditions", "documents", "procedure", "time", "partners", "fees", "notes"]

# ---- keyword tables (matched against norm(question)) ----
DOC_KEYWORDS = {
    "passport": ["جواز", "باسبور", "الباسبور", "passport"],
    "family_book": ["دفتر", "عائله", "عيله"],
    "id_card": ["هويه", "هويت", "بطاقه", "بطاقت", "البطاقه الذكيه", "الهويه", "كرت", "id"],
}
SITUATION_KEYWORDS = {
    "lost": ["فاقد", "ضاع", "ضايع", "ضيعت", "ضيع", "فقدت", "فقد", "مفقود", "انسرق", "سرق", "انفقد"],
    "damaged": ["تالف", "تلف", "تلفان", "خربان", "خرب", "انكسر", "مكسور", "انقطع", "تمزق", "ممزق",
                "مشقوق", "انشق", "مبلول", "انبل", "اهترى"],
    "renewal": ["تجديد", "جدد", "اجدد", "بجدد", "منتهي", "انتهى", "انتهت", "خلص", "مخلص"],
    "first_issue": ["اول مره", "لاول مره", "لاول", "اول اشي", "اول بطاقه", "اول جواز", "اول دفتر", "اصدار", "ما طلعت", "ما اطلعت", "ما عملت", "تزوجت", "تزوج", "عقد الزواج", "مولود", "ما عندي", "ماعندي"],
}
WEAK_SITUATION_KEYWORDS = {"first_issue": ["جديد", "اطلع"]}  # count only if no strong keyword
FIELD_KEYWORDS = {
    "fees": ["رسوم", "سعر", "تكلفه", "بكلف", "يكلف", "كلفه", "دينار", "مصاري", "فلوس", "ادفع",
             "بدفع", "يدفع", "ببلاش", "مجاني", "مجانا", "مستعجل", "مستعجله", "غرامه", "قديش بدفع", "كم بدفع", "قديش حقه", "حق"],
    "documents": ["تعهد", "كفاله", "اوراق", "ورق", "وثائق", "مستندات", "مطلوب", "بلزم", "بلزمني", "بحتاج", "احتاج",
                  "اجيب", "احضر", "صور", "صوره", "اوراقي"],
    "time": ["اسرع", "مده", "وقت", "يستغرق", "بياخذ", "ياخذ", "بطول", "دقيقه", "دقايق", "ساعه", "متى", "قديش بده"],
    "places": ["وين", "اين", "مكان", "اماكن", "سفاره", "قنصليه", "برا البلد", "خارج", "بره", "مكتب", "فرع"],
    "conditions": ["قصد", "متعمد", "عمدا", "شو بصير", "شو بيصير", "يوافق", "وكاله", "توكيل", "بيحقله", "شروط", "شرط", "شخصيا", "عمر", "سن", "يحق", "مسموح", "موافقه", "بدون", "وكيل", "بالنيابه", "عني"],
    "procedure": ["خطوات", "اجراءات", "طريقه", "كيف", "شو بعمل"],
    "target": ["الفئه", "يستفيد"],
    "partners": ["شركاء", "جهات", "جهه"],
}
OFF_TOPIC = ["تذكره", "طيران", "شهاده", "جامعه", "تصديق", "فيزا", "تاشيره", "رخصه", "سياره", "مخالف"]
CLARIFY_FIELDS = {"fees", "documents", "time", "conditions", "procedure"}
# regex overrides: "جواز" not inside "جوازات" (agency name); "id" and "حق" are whole words

# English and Arabizi (Arabic in Latin letters, 2=ء 3=ع 5=خ 7=ح) keywords, merged into the tables above.
# Latin keywords match at a word start (optionally after el/il/al/l/b/w), any suffix allowed.
LATIN_DOC = {
    "passport": ["passport", "pasport", "passprt", "jawaz", "jawaaz", "jwaz", "basbor", "baspor", "basbort", "paspor"],
    "family_book": ["family book", "family booklet", "family registry", "family record", "family register",
                    "daftar", "dafter", "3eleh", "3eleh", "3ele", "3ayle", "3ayleh", "3a2ile", "3a2ileh", "3ayla",
                    "3aileh", "3a2ela", "3elti"],
    "id_card": ["national id", "identity card", "smart card", "smart id", "civil id", "id card", "card",
                "hawiye", "hawiyeh", "hawiyye", "hawiya", "hawya", "hawye", "hwye", "hwyti", "hawiyti", "hawiti",
                "hwiyti", "hawyti", "hawiyt", "hwyt", "hawyt", "beta2t", "bita2t", "betaqt", "beta2a", "bita2a", "betaqa", "bitaqa", "bitaka", "betaka", "kart"],
}
LATIN_SITUATION = {
    "lost": ["lost", "lose", "losing", "stolen", "missing", "can't find", "cant find", "misplaced",
             "da3", "daa3", "dayya3", "daya3", "day3", "dy3", "m2foode", "mafqood", "mafqoud", "fa2ed", "faqed",
             "insara2", "ansara2", "nsara2", "sara2o", "sare2"],
    "damaged": ["damage", "broken", "broke", "torn", "ripped", "wet", "ruined", "destroyed", "cracked", "faded",
                "5arban", "kharban", "5irib", "5reb", "5areb", "talef", "tálef", "tlef", "tilef", "inkasar",
                "ankasar", "maksoor", "maksour", "t2a6a3", "it2atta3", "t2atta3", "mamzoo2", "mamzou2", "tmazza2",
                "itmazza2", "inbal", "mabloul", "mablool"],
    "renewal": ["jadadt", "jaddadt", "jaddad", "jadad", "renew", "expired", "expire", "expiring", "ran out", "out of date", "tajdeed", "tajdid",
                "ajadded", "ajaded", "ajadid", "jadded", "jaded", "bjadded", "bajadded", "montahi", "muntahi",
                "mintihi", "5ales", "5ilis", "khales"],
    "first_issue": ["first time", "first-time", "first", "1st time", "never had", "never got", "never issued", "awal", "awal marra", "awal mara",
                    "2awal marra", "2awal mara", "awwal marra", "awwal mara", "la2awal", "lawal", "ma 3ndi",
                    "ma3ndi", "ma 3indi", "ma3indi"],
}
LATIN_WEAK = {"first_issue": ["new", "issue", "jdeed", "jdid", "atla3", "a6la3", "ttla3", "6ala3"]}
LATIN_FIELDS = {
    "fees": ["fee", "cost", "price", "pay", "charge", "mista3j", "msta3j", "ista3jal", "sta3jel", "dinar", "jd", "money", "cheap", "free", "express",
             "urgent", "fine", "penalty", "rsoom", "rusoom", "rsom", "rosoom", "rsum", "se3r", "si3r", "bedfa3", "badfa3", "adfa3", "bdfa3", "dfa3", "ndfa3",
             "masari", "msari", "flous", "floos", "bkalef", "btkalef", "bikallef", "ghrame", "8arame", "gharame",
             "mista3jel", "msta3jel", "mesta3jel"],
    "documents": ["pledge", "guarantee", "bond", "kafale", "kafala", "ta3ahhod", "ta3ahod", "document", "docs", "paper", "paperwork", "required", "need", "bring", "photo", "picture",
                  "awra2", "awraq", "wara2", "wra2", "wathayi2", "wathayeq", "wathaye2", "mustanadat", "bl7aje",
                  "b7taj", "ba7taj", "a7taj", "bi7taj", "blzam", "bilzam", "bilzamni", "blzamni", "ajeeb", "jeeb",
                  "sora", "suwar", "sowar", "swar", "soura", "sura", "9ora", "9owar"],
    "time": ["asra3", "fastest", "faster", "how long", "time", "take", "minute", "hour", "day", "when", "wait", "quick", "fast", "wa2t", "wa2et",
             "byakhod", "biyakhod", "byo5od", "by5od", "byakhd", "mudde", "mudda", "modde", "emta", "imta", "aimta",
             "da2i2a", "d2ay2", "sa3a"],
    "places": ["where", "place", "location", "embassy", "consulate", "abroad", "outside", "office", "branch",
               "wen", "wein", "wain", "ween", "makan", "mkan", "safara", "sefara", "2onsolia", "qunsuliya", "barra",
               "5arej", "kharej", "maktab"],
    "conditions": ["on purpose", "intentional", "deliberate", "2asd", "3amdan", "what happens", "shu bseer",
                   "shu biseer", "ywaf2", "bwaf2", "mwaf2", "waf2", "wakale", "tawkeel", "msmoo7", "masmoo7", "msmo7",
                   "mesmoo7", "ye7a2", "y7a2", "condition", "requirement", "allowed", "in person", "age", "approval", "permission", "consent",
                   "proxy", "on behalf", "someone else", "husband", "guardian", "shroot", "shuroot", "shart",
                   "mwafa2a", "mowafa2a", "mwafa2et", "wakeel", "wkale", "wakkel", "3anni", "shakhsiyan", "3omri",
                   "3umri"],
    "procedure": ["steps", "procedure", "process", "how do i", "how to", "how can i", "5utuwat", "5twat",
                  "ijra2at", "ejra2at", "kif", "keef", "kaif"],
    "target": ["eligible"],
    "partners": ["partner", "agencies"],
}
LATIN_OFF_TOPIC = ["ticket", "flight", "visa", "driving", "license", "licence", "birth certificate",
                   "death certificate", "university", "degree", "attestation", "restaurant", "weather",
                   "working hours", "opening hours", "open on", "residency", "residence permit", "car registration",
                   "diplomatic", "tathkara", "tazkara", "tayyara", "ta2era", "ra5sa", "rokhsa", "fiza", "fisa",
                   "jam3a", "mat3am", "ta2s", "dawam", "شهاده ميلاد", "دبلوماسي", "دوام", "بيفتح", "اقامه", "طقس",
                   "مطعم", "منسف"]
for _table, _extra in ((DOC_KEYWORDS, LATIN_DOC), (SITUATION_KEYWORDS, LATIN_SITUATION),
                       (WEAK_SITUATION_KEYWORDS, LATIN_WEAK), (FIELD_KEYWORDS, LATIN_FIELDS)):
    for _key, _words in _extra.items():
        _table.setdefault(_key, []).extend(_words)
OFF_TOPIC = OFF_TOPIC + LATIN_OFF_TOPIC
NOTES_INTENT = ["خلال", "مهله", "within", "deadline", "5ilal", "khilal", "mohle"]
WEAK_FIELD_KEYWORDS = {
    "fees": ["قديش", "كم", "how much", "2adesh", "adesh", "adeesh", "2adeesh", "addesh", "kam"],
    "target": ["مين", "لمين", "who", "meen", "la meen"],
}
_LATIN_PREFIX = r"(?<![a-z0-9'])(?:el|il|al|l|b|w|wl|bl|fl|3al|bn|bt|by|ba|bi|n|t|y|a|ma)?"
SPECIAL = {"jd": r"(?<![a-z])jd(?![a-z])", "time": r"(?<![a-z\-])(?<!first )(?<!second )(?<!third )(?<!1st )(?<!2nd )(?<!3rd )(?<!this )(?<!last )(?<!next )(?<!every )(?<!one )(?<!first-)time",  # "second time" is not a time question
           "لاول": "(?<!من ا)لاول", "جواز": "جواز(?!ات)", "id": r"\bid\b", "حق": r"\bحق\b"}

# ---- prompts ----
SYSTEM_PROMPT = (
    "أنت مساعد دائرة الأحوال المدنية والجوازات في الأردن. أجب بالعربية الفصحى المبسطة باختصار شديد، "
    "بجملة كاملة واضحة، عن المطلوب في السؤال فقط، معتمداً حصراً على «المعلومات المتاحة» (نتائج البحث).\n"
    "- انسخ الأرقام والمبالغ والمدد والشروط كما وردت حرفياً وبالأرقام، ولا تحسب ولا تستنتج أرقاماً جديدة.\n"
    "- إذا تعددت الرسوم حسب الحالة (العمر، الصلاحية، داخل الأردن أو خارجه، عدد مرات الفقدان) فاختر السطر المطابق لحالة السائل فقط؛ "
    "وإن لم تتضح حالته فاذكر الحالات باختصار.\n"
    "- بنود الملاحظات قواعد مستقلة تنطبق على الجميع ما لم يذكر البند حالة بعينها؛ اذكر البند فقط إذا كان يغيّر الجواب. "
    "إذا قيّد بند في الملاحظات معلومة عامة (مثل موعد استلام الوثيقة أو مهلة التجديد) فالملاحظة هي المعتمدة في الجواب.\n"
    "- إذا ذكر السائل معلومة خاطئة أو سأل للتأكد (صح؟ / right?) فقل إنها غير صحيحة واذكر المعلومة الصحيحة من النتائج "
    "(مثل المدة أو الرسوم الصحيحة، أو أماكن التقديم الصحيحة إذا ذكر مكاناً غير مذكور فيها) بدلاً من قول إن المعلومة غير متوفرة.\n"
    "- إن لم تجد الجواب فقل إن المعلومة غير متوفرة لديك.\n"
    "- لا تذكر عبارة «المعلومات المتاحة» ولا أرقام المصادر."
)
CLARIFY_CASE = (
    "السؤال التالي غير واضح، لأنه لا يحدد الحالة المقصودة للوثيقة: {docs}. "
    "الحالات الممكنة: لأول مرة، أو تجديد، أو بدل فاقد، أو بدل تالف. "
    "اطلب من السائل توضيح الحالة بسؤال توضيحي واحد قصير ومهذب فقط، واذكر فيه الخيارات.\n\nالسؤال: {q}"
)
CLARIFY_DOC = (
    "السؤال التالي غير واضح، لأنه لا يحدد الوثيقة المقصودة. "
    "الوثائق الممكنة: جواز السفر، دفتر العائلة، البطاقة الذكية. "
    "اطلب من السائل تحديد الوثيقة بسؤال توضيحي واحد قصير ومهذب فقط، واذكر فيه الخيارات.\n\nالسؤال: {q}"
)
OUT_OF_SCOPE = (
    "السؤال التالي خارج نطاق الخدمات المتوفرة لديك (جواز السفر، دفتر العائلة، البطاقة الذكية). "
    "اعتذر بلطف في جملة أو جملتين، وقل إن هذه المعلومة غير متوفرة لديك، "
    "وإنك تستطيع المساعدة في الخدمات المذكورة فقط. لا تجب عن السؤال ولا تخمّن.\n\nالسؤال: {q}"
)
REFUSE = (
    "الطلب التالي غير قانوني، أو يطلب بيانات شخصية عن أشخاص آخرين، ولا يمكنك المساعدة فيه. "
    "ارفض بلطف وباختصار في جملة أو جملتين، دون أي تفاصيل أو أرقام، "
    "واذكر أنك تستطيع المساعدة في الخدمات الرسمية لجواز السفر ودفتر العائلة والبطاقة الذكية.\n\nالطلب: {q}"
)
SOURCE_RE = re.compile(r"\s*[،,]?\s*(?:وفق\S*|بحسب|حسب|بناء\S*\s+على)\s+\S*معلومات\s+(?:المتاحة|المتوفرة|المقدمة)")
NUM_WRAP_RE = re.compile(r"\${1,2}\s*([\d.,]+)\s*\${1,2}|\[\s*([\d.,]+)\s*\]|\\\(\s*([\d.,]+)\s*\\\)")
LABEL_RE = re.compile(r"^\s*(?:الجواب|الإجابة|الاجابة|الرد|answer)\s*[:：]\s*", re.IGNORECASE)

# ---- normalisation and keyword compilation ----
_NORM = {cp: None for cp in range(0x064B, 0x0653)}  # tashkeel U+064B-U+0652
_NORM[0x0640] = None  # tatweel
for _src, _dst in (("أإآٱ", "ا"),  # أ إ آ ٱ -> ا
                   ("ة", "ه"),  # ة -> ه
                   ("ى", "ي"),  # ى -> ي
                   ("ؤ", "و"),  # ؤ -> و
                   ("ئ", "ي")):  # ئ -> ي
    _NORM.update({ord(c): _dst for c in _src})
_NORM.update({0x0660 + i: str(i) for i in range(10)})  # Arabic-Indic digits -> 0-9


def norm(s):
    """Normalise Arabic text for keyword matching only (never for output)."""
    return s.translate(_NORM).lower()


def _kw_re(kw):
    """Zero-width regex, so finditer also reports overlapping occurrences."""
    k = norm(kw)
    if k in SPECIAL:
        return re.compile("(?=" + SPECIAL[k] + ")")
    if k.isascii():  # Latin word: must start a word (after an optional Arabizi article/prefix)
        return re.compile("(?=" + _LATIN_PREFIX + re.escape(k) + ")")
    return re.compile("(?=" + re.escape(k) + ")")


def _compile(table):
    return {key: [_kw_re(w) for w in words] for key, words in table.items()}


DOC_RE, SIT_RE = _compile(DOC_KEYWORDS), _compile(SITUATION_KEYWORDS)
WEAK_RE, FIELD_RE = _compile(WEAK_SITUATION_KEYWORDS), _compile(FIELD_KEYWORDS)
WEAK_FIELD_RE = _compile(WEAK_FIELD_KEYWORDS)


def _hits(qn, table):
    """(position, key) for every keyword occurrence in normalised text qn."""
    return [(m.start(), key) for key, pats in table.items() for p in pats for m in p.finditer(qn)]


# ---- routing ----
NOT_A_DOC = [norm(w) for w in ("الهوية المقدسية", "الهويات المقدسية", "هوية مقدسية", "هويه مقدسيه")]


def route(question):
    """[(doc_type, situation or None)] in order of first appearance."""
    qn = norm(question)
    for phrase in NOT_A_DOC:  # e.g. "Jerusalem ID holders" is a fee category, not the ID card service
        qn = qn.replace(phrase, " " * len(phrase))
    docs = _hits(qn, DOC_RE)
    sits = _hits(qn, SIT_RE) or _hits(qn, WEAK_RE)
    if len({d for _, d in docs}) == 1 and any(sd in ("lost", "damaged") for _, sd in sits):  # "lost for the first time" is not first issue
        sits = [h for h in sits if h[1] != "first_issue"] or sits
    out = []
    for doc in dict.fromkeys(d for _, d in sorted(docs)):
        dpos = [p for p, d in docs if d == doc]
        sit = None
        if sits and len({d for _, d in docs}) == 1:  # one doc: every situation named (comparisons)
            for sit in dict.fromkeys(sd for _, sd in sorted(sits)):
                out.append((doc, sit))
            continue
        if sits:  # situation keyword closest (by character distance) to any mention of this doc
            sit = min(sits, key=lambda h: (min(abs(h[0] - p) for p in dpos), h[0]))[1]
        out.append((doc, sit))
    return out


def first_situation(question):
    """Earliest situation keyword in the question (weak keywords as fallback), or None."""
    qn = norm(question)
    hits = _hits(qn, SIT_RE) or _hits(qn, WEAK_RE)
    return min(hits)[1] if hits else None


def keyword_fields(question):
    """Field keys with a keyword hit (notes is never keyword-matched).

    Generic words ("how much", "kam", "who") only count when no specific field word matched.
    """
    qn = norm(question)
    strong = [f for f in FIELD_ORDER if f in FIELD_RE and any(p.search(qn) for p in FIELD_RE[f])]
    if strong:
        return strong
    if any(_kw_re(w).search(qn) for w in NOTES_INTENT):  # deadlines live in the notes, not in "time taken"
        return ["notes"]
    return [f for f in FIELD_ORDER if f in WEAK_FIELD_RE and any(p.search(qn) for p in WEAK_FIELD_RE[f])]


# ---- data ----
def _clean(lines):
    """Strip lines, collapse space/tab runs, drop empty lines, join with newlines."""
    cleaned = (re.sub(r"[ \t]+", " ", ln.strip()) for ln in lines)
    return "\n".join(ln for ln in cleaned if ln)


def parse_fields(text):
    """Split one service file into {field_key: cleaned content}."""
    raw, key = {}, None
    for line in text.split("\n"):
        s = line.lstrip()
        hit = next((k for k, label in HEADERS.items() if s.startswith(label)), None)
        if hit:  # header line: content starts right after the label
            key = hit
            raw[key] = [s[len(HEADERS[key]):]]
        elif key:
            raw[key].append(line)
    return {k: _clean(lines) for k, lines in raw.items()}


def load_chunks(data_dir):
    """{(service_key, field): (chunk_text, content)}; skips notes whose content is 'لا يوجد'."""
    chunks = {}
    for key, name in SERVICES.items():
        try:
            text = (Path(data_dir) / f"{key}.txt").read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:  # missing or unreadable: skip this service
            print(f"warning: skipping {key}.txt ({exc})", file=sys.stderr)
            continue
        fields = parse_fields(text)
        for field in FIELD_ORDER:
            content = fields.get(field)
            if content is None or (field == "notes" and content == "لا يوجد"):
                continue
            chunks[(key, field)] = (f"{name} - {HEADERS[field]}: {content}", content)
    return chunks


# ---- embeddings (bge-m3 via Ollama) ----
def _post(path, payload, timeout=300):
    body = json.dumps(payload).encode("utf-8")
    for attempt in range(2):  # one retry after a short pause on connection-level failures
        req = urllib.request.Request(OLLAMA + path, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, socket.timeout, ConnectionResetError):
            if attempt:
                raise
            time.sleep(3)


def embed(texts):
    """Vectors for texts, at most 16 texts per request."""
    vecs = []
    for i in range(0, len(texts), 16):
        vecs += _post("/api/embed", {"model": EMBED_MODEL, "input": texts[i:i + 16]})["embeddings"]
    return vecs


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def build_vectors(chunks):
    """Embed all chunks at startup; None means keyword-only mode."""
    keys = list(chunks)
    try:
        vecs = embed([chunks[k][0] for k in keys])
    except Exception as exc:  # bge-m3 missing or Ollama not reachable
        print(f"warning: embeddings unavailable ({exc}); keyword-only mode", file=sys.stderr)
        return None
    return dict(zip(keys, vecs))


# ---- planning: mode, services, fields, contexts (no LLM call) ----
def _content(chunks, svc, field):
    return chunks[(svc, field)][1] if (svc, field) in chunks else None


def select_fields(services, kw, qvec, chunks, vectors):
    """Keyword fields, else the top-2 non-notes chunks by cosine, else the core fields; notes always."""
    fields = set(kw)
    if not fields and qvec is not None:
        scored = sorted(((cosine(qvec, vectors[k]), k[1]) for k in chunks
                         if k[0] in services and k[1] != "notes" and k in vectors),
                        key=lambda t: -t[0])
        fields = {f for _, f in scored[:2]}
    if not fields:  # no keyword match and no usable embedding
        fields = {"documents", "fees", "time", "conditions"}
    if fields and fields <= {"places", "target", "partners", "procedure"}:
        return [f for f in FIELD_ORDER if f in fields]  # notes only pad these answers
    return [f for f in FIELD_ORDER if f in fields or f == "notes"]


def note_items(content):
    """Split a notes field into standalone items ("1. ..." / "- ..."), merging continuation lines."""
    items = []
    for line in content.split("\n"):
        m = re.match(r"^\s*(?:\d+\s*[.\-)]|[-•])\s*", line)
        if m or not items:
            items.append(line[m.end():] if m else line)
        else:
            items[-1] += " " + line
    return [it.strip() for it in items if it.strip()]


def build_contexts(services, fields, chunks):
    """Chunk texts in service/field order; notes become one context per item so each rule stands alone."""
    out = []
    for s in services:
        for f in FIELD_ORDER:
            if f not in fields or (s, f) not in chunks:
                continue
            if f == "notes":
                out += [f"{SERVICES[s]} - {HEADERS[f]}: {it}" for it in note_items(chunks[(s, f)][1])]
            else:
                out.append(chunks[(s, f)][0])
    return out


REFUSE_KEYWORDS = ["زور", "تزوير", "مزور", "رشوه", "رشوة", "اختراق", "fake", "forge", "forged", "counterfeit",
                   "bribe", "hack", "zawwer", "zawer", "bzawwer", "mzawwar", "tazweer", "rashwe", "rashwa",
                   "رقم هويه", "رقم الهويه", "الرقم الوطني ل", "عنوان بيت", "national id number", "id number of",
                   "address of", "phone number of"]
_NATIONALITIES = [("سوري", "syrian"), ("مصري", "egyptian"), ("عراقي", "iraqi"), ("سعودي", "saudi"),
                  ("لبناني", "lebanese"), ("امريكي", "american"), ("بريطاني", "british"), ("تركي", "turkish"),
                  ("كندي", "canadian"), ("اماراتي", "emirati"), ("كويتي", "kuwaiti"), ("قطري", "qatari")]
HARD_OFF_TOPIC = ["مؤقت", "temporary", "دبلوماسي", "diplomatic", "us passport", "uk passport"] + [
    p for ar, en in _NATIONALITIES for p in (f"جواز {ar}", f"الجواز ال{ar}", f"جواز سفر {ar}", f"هويه {ar}",
                                             f"{en} passport", f"{en} id")]


def guard_mode(qn):
    """'refuse' for illegal or personal-data requests, 'out_of_scope' for services not in the data, else None."""
    if any(_kw_re(w).search(qn) for w in REFUSE_KEYWORDS):
        return "refuse"
    if any(norm(w) in qn for w in HARD_OFF_TOPIC):
        return "out_of_scope"
    return None


def plan(question, last, chunks, vectors, prev_fields=None):
    """Mode, services, fields and contexts for one question.

    last: (doc, situation) pairs of the previous message in this chat that had doc types, or None.
    """
    qn = norm(question)
    guard = guard_mode(qn)
    if guard:  # illegal / personal-data requests and services we don't cover: never route to documents
        return {"pairs": [], "docs": [], "best_sim": None, "mode": guard,
                "services": [], "fields": [], "contexts": []}
    pairs = route(question)
    off_topic = any(norm(w) in qn for w in OFF_TOPIC)
    if not pairs and last and not off_topic:  # follow-up: combine new situation with history doc, else inherit
        sit = first_situation(question)
        pairs = [(d, sit) for d, _ in last] if sit else list(last)
    kw = keyword_fields(question)
    if prev_fields and not (set(kw) - {"conditions"}):  # bare follow-up: keep asking about the same thing
        kw = [f for f in FIELD_ORDER if f in set(kw) | (set(prev_fields) - {"notes"})]
    try:
        qvec = embed([question])[0] if vectors is not None else None
    except Exception as exc:  # Ollama down or bge-m3 missing: keyword-only for this question
        print(f"warning: query embedding failed ({exc})", file=sys.stderr)
        qvec = None
    res = {"pairs": pairs, "docs": [], "best_sim": None}
    answered = [(d, s) for d, s in pairs if s]
    if answered:  # at least one (doc, situation) is known
        services = [f"{d}_{s}" for d, s in answered]
        fields = select_fields(services, kw, qvec, chunks, vectors)
        mode = "answer"
    elif pairs:  # doc known, situation unknown: answer only if the 4 cases agree
        groups = {d: [f"{d}_{s}" for s in SITUATIONS] for d, _ in pairs}
        fields = select_fields([s for g in groups.values() for s in g], kw, qvec, chunks, vectors)
        fields = [f for f in fields if f != "notes"]  # notes always differ; compare real fields only
        same = bool(fields) and all(len({_content(chunks, s, f) for s in g}) == 1
                                    for g in groups.values() for f in fields)
        services = [f"{d}_renewal" for d in groups] if same else []
        mode = "answer" if same else "clarify"
        res["docs"] = list(groups)
    else:  # no doc type and no history
        services, fields, mode = [], kw, "out_of_scope"
        if qvec is not None and vectors:
            res["best_sim"] = max(cosine(qvec, v) for v in vectors.values())
        triggered = first_situation(question) is not None or bool(set(kw) & CLARIFY_FIELDS)
        if triggered and not off_topic:
            mode = "clarify"
    res.update(mode=mode, services=services, fields=fields,
               contexts=build_contexts(services, fields, chunks) if mode == "answer" else [])
    if mode == "answer" and not res["contexts"]:  # nothing to ground an answer on: ask for clarification
        res.update(mode="clarify", docs=list(dict.fromkeys(d for d, _ in pairs)))
    return res


# ---- LLM and main loop ----
def _focus_hint(p):
    """On comparisons, remind the model to answer for every service (it tends to answer only the first)."""
    if len(p.get("services", [])) < 2:
        return ""
    return "\n(أجب عن كل من: " + " و ".join(SERVICES[s] for s in p["services"]) + ")"


# Case cues in the question -> which fee lines apply (age, expiry, abroad, military, full pages, nth loss, fine)
_CUES = {
    "expired": ["منتهي", "انتهى", "انتهت", "expired", "montahi", "muntahi", "intaha", "5ales"],
    "valid": ["مش منتهي", "ما انتهى", "لسا ما", "لسا ساري", "ساري", "not expired", "still valid", "valid",
              "mish montahi", "lissa sari", "sari"],
    "abroad": ["خارج", "برا البلد", "بره البلد", "abroad", "outside jordan", "السفاره", "embassy", "safara", "الامارات",
               "قطر", "السعوديه", "الكويت", "كندا", "المانيا", "امريكا", "بريطانيا", "تركيا", "uae", "qatar", "saudi",
               "kuwait", "canada", "germany", "usa", "emarat", "2a6ar", "bl emarat"],
    "inside": ["داخل", "بالاردن", "in jordan", "عمان", "الزرقاء", "الزرقا", "اربد", "zarqa", "amman", "irbid", "zar2a"],
    "military": ["عسكري", "القوات المسلحه", "جيش", "الامن العام", "military", "army", "soldier", "3askari"],
    "full": ["امتلت", "ممتلئ", "full", "الصفحات", "pages", "sf7at", "safa7at"],
    "later": ["ثاني", "تاني", "ثالث", "تالت", "second", "2nd", "third", "3rd", "tani", "talet", "talt"],
    "first": ["اول مره", "لاول مره", "المره الاولى", "first time", "awal marra"],
    "fine": ["غرامه", "تاخير", "late", "fine", "penalty", "8arame", "gharame", "ta25eer", "8aramet"],
}
_AGE_RE = re.compile(r"(?:عمر\S*|3omr\S*|aged?|i'?m|i am)\D{0,6}(\d{1,2})\b|(\d{1,2})\s*(?:سنه|سنين|سنوات|years?|sneen|sene)")


def _fee_line_score(line, cues, age):
    """How well one fee line matches the asker's case (higher is better; 0 = neutral)."""
    ln, score = norm(line), 0
    under16 = "دون" in ln and ("16" in ln or "السادسه عشر" in ln)
    over16 = "فوق" in ln and ("16" in ln or "السادسه عشر" in ln)
    expired = "منتهي" in ln and "غير المنتهي" not in ln and "غير منتهي" not in ln
    valid = "غير المنتهي" in ln or "غير منتهي" in ln or "ساري" in ln
    if age is not None:
        score += (2 if under16 else -3 if over16 else 0) if age < 16 else (2 if over16 else -3 if under16 else 0)
    if "expired" in cues and "valid" not in cues:
        score += 2 if expired else -3 if valid else 0
    if "valid" in cues:
        score += 2 if valid else -3 if expired else 0
    if "abroad" in cues:
        score += 2 if "خارج" in ln else -2 if "داخل" in ln else 0
    elif "inside" in cues:
        score += 2 if "داخل" in ln else -3 if "خارج" in ln else 0
    if "القوات المسلحه" in ln:
        score += 3 if "military" in cues else -1
    if "full" in cues and "الممتلي" in ln:  # norm() turns ئ into ي
        score += 3
    later_line = "تلي" in ln or "الثانيه" in ln
    first_line = "المره الاولى" in ln
    if "later" in cues:
        score += 2 if later_line else -3 if first_line else 0
    elif "first" in cues:
        score += 2 if first_line else -3 if later_line else 0
    if "fine" in cues and "غرامه" in ln:
        score += 2
    return score


def select_fee_lines(lines, question):
    """Keep only the fee lines matching the asker's case; all lines when the question gives no case cues."""
    qn = norm(question)
    cues = {k for k, words in _CUES.items() if any(norm(w) in qn for w in words)}
    m = _AGE_RE.search(qn)
    age = int(next(g for g in m.groups() if g)) if m else None
    if not cues and age is None or len(lines) < 2:
        return lines
    scores = [_fee_line_score(ln, cues, age) for ln in lines]
    best = max(scores)
    return [ln for ln, sc in zip(lines, scores) if sc == best] if best > 0 else lines


def _split_fee_lines(contexts, question=""):
    """One document per fee line (only the lines matching the asker's case), so the model picks the right one."""
    tag, out = f" - {HEADERS['fees']}: ", []
    for c in contexts:
        if tag in c and "\n" in c:
            head, body = c.split(tag, 1)
            lines = select_fee_lines([ln for ln in body.split("\n") if ln.strip()], question)
            out += [f"{head}{tag}{ln}" for ln in lines]
        else:
            out.append(c)
    return out


ARABIZI_WORDS = {"shu", "shoo", "sho", "bdi", "biddi", "badi", "wen", "wein", "kif", "keef", "adesh", "2adesh", "kam",
                 "ya", "3shan", "lazem", "ma3", "mn", "ana", "inta", "enta", "hay", "hada", "marhaba", "mar7aba",
                 "habibi", "ahlan", "salam", "m3lim", "mu3allem", "el", "elli", "illi", "w", "b", "eza", "iza", "law"}
LANG_RULE = {
    "en": "\n- The user wrote in English: answer in clear, short English (keep numbers exactly as in the documents).",
    "ar": "\n- أجب باللغة العربية دائماً، حتى لو كتب السائل بعض الكلمات بالإنجليزية أو بحروف لاتينية.",
}


def detect_lang(question):
    """'en' for plain English questions; Arabic script, Arabizi or mixed questions get 'ar'."""
    arabic = len(re.findall(r"[\u0600-\u06FF]", question))
    latin = re.findall(r"[A-Za-z0-9']+", question)
    if arabic >= 3 or not latin:
        return "ar"
    words = [w.lower() for w in latin]
    arabizi = sum(1 for w in words if w in ARABIZI_WORDS or re.search(r"[a-z][2357][a-z]|^[2357][a-z]|[a-z][2357]$", w))
    return "ar" if arabizi >= max(1, len(words) // 6) else "en"


def _build_messages(p, question, history, grounded=GROUNDED):
    msgs = [{"role": "system", "content": SYSTEM_PROMPT + LANG_RULE[detect_lang(question)]}]
    if p["mode"] == "answer":
        for q, a in history[-2:]:  # previous 2 turns of this chat
            msgs += [{"role": "user", "content": q}, {"role": "assistant", "content": a}]
        if grounded:  # Command-R native RAG: documents arrive as a search tool result
            tag = f" - {HEADERS['notes']}: "  # notes first: the model otherwise lets general fields override them
            fee_tag = f" - {HEADERS['fees']}: "
            first = (lambda c: fee_tag in c) if "fees" in p["fields"] else (lambda c: tag in c)
            ordered = [c for c in p["contexts"] if first(c)] + [c for c in p["contexts"] if not first(c)]
            docs = [{"id": f"doc_{i}", "text": t} for i, t in enumerate(_split_fee_lines(ordered, question))]
            msgs += [{"role": "user", "content": question + _focus_hint(p)},
                     {"role": "assistant", "content": "",
                      "tool_calls": [{"function": {"name": "search_services", "arguments": {"query": question}}}]},
                     {"role": "tool", "content": json.dumps(docs, ensure_ascii=False)[1:-1].replace('"', "'")}]
            return msgs
        info = "\n\n".join(f"- {c}" for c in p["contexts"])
        text = f"المعلومات المتاحة:\n{info}\n\nالسؤال: {question}{_focus_hint(p)}"
    elif p["mode"] == "clarify" and p["docs"]:
        text = CLARIFY_CASE.format(docs=" و ".join(DOC_NAMES[d] for d in p["docs"]), q=question)
    elif p["mode"] == "clarify":
        text = CLARIFY_DOC.format(q=question)
    elif p["mode"] == "refuse":
        text = REFUSE.format(q=question)
    else:
        text = OUT_OF_SCOPE.format(q=question)
    msgs.append({"role": "user", "content": text})
    return msgs



def build_messages(p, question, history, grounded=GROUNDED):
    """Chat messages for one question; English questions get an explicit answer-in-English cue."""
    msgs = _build_messages(p, question, history, grounded=grounded)
    if detect_lang(question) == "en":
        last_user = max(i for i, m in enumerate(msgs) if m["role"] == "user")
        msgs[last_user] = dict(msgs[last_user], content="(Reply in English.)\n" + msgs[last_user]["content"] + "\n\n(Answer in English.)")
    return msgs

def ask(messages):
    payload = {"model": MODEL, "messages": messages, "stream": False,
               "keep_alive": "30m", "options": OPTIONS}
    if any(m["role"] == "tool" for m in messages):
        payload["tools"] = [SEARCH_TOOL]
    reply = _post("/api/chat", payload, timeout=900)["message"]["content"].strip()
    reply = LABEL_RE.sub("", reply, count=1).replace("**", "")
    reply = NUM_WRAP_RE.sub(lambda m: next(g for g in m.groups() if g), reply)  # [25] / $$25$$ -> 25
    reply = SOURCE_RE.sub("", reply)
    reply = re.sub(r"(?i)\s*,?\s*(?:according to|based on) the (?:available|provided) "
                   r"(?:information|documents|search results|data)\s*,?", " ", reply)  # drop "according to the available information" and [n] refs
    return re.sub(r"\s+([،.])", r"\1", reply).strip().lstrip("،,: ").strip()


def save(path, data):
    """Atomic write (temp file, then os.replace); falls back to a direct write. Never raises."""
    try:
        text = json.dumps(data, ensure_ascii=False, indent=2)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        try:
            os.replace(tmp, path)
        except OSError:  # e.g. PermissionError on replace: write the file directly instead
            path.write_text(text, encoding="utf-8")
    except Exception as exc:
        print(f"warning: could not save {path} ({exc})", file=sys.stderr)


def _words(text):
    """Normalised content words (3+ letters) and numbers, for answer/context overlap."""
    return {w for w in re.findall(r"\w+", norm(text)) if len(w) >= 3 or w.isdigit()}


def used_contexts(contexts, answer):
    """Keep every field chunk; keep a notes item only if the answer reflects it (shared number or ~35% words)."""
    note_tag = f" - {HEADERS['notes']}: "
    aw, kept = _words(answer), []
    for c in contexts:
        if note_tag in c:
            cw = _words(c.split(note_tag, 1)[1])
            nums = {w for w in cw if w.isdigit()}
            if not cw or not ((nums & aw) or len(cw & aw) / len(cw) >= 0.35):
                continue
        kept.append(c)
    return kept


def _chat_messages(data):
    """Per chat, its dict messages in order; non-dict chats and messages are skipped (never raises)."""
    chats = data.get("chats") if isinstance(data, dict) else None
    result = []
    for chat in (chats if isinstance(chats, list) else []):
        msgs = chat.get("messages") if isinstance(chat, dict) else None
        if isinstance(msgs, list):
            result.append([m for m in msgs if isinstance(m, dict)])
    return result


NUMBER_WORDS = {
    "واحد": ["1"], "اثنين": ["2"], "اثنان": ["2"], "دينارين": ["2"], "ديناران": ["2"], "صورتين": ["2"],
    "اسبوعين": ["2", "14"], "شهرين": ["2"], "ثلاث": ["3"], "اربع": ["4"], "خمس": ["5"], "عشر": ["10"],
    "السادسة عشر": ["16"], "السادسه عشر": ["16"], "الثامنة عشر": ["18"], "الثامنه عشر": ["18"],
    "عشرين": ["20"], "ثلاثين": ["30"], "خمسين": ["50"], "مائة": ["100"], "مئة": ["100"],
}


def _numbers(text):
    """Numbers in text, ignoring list markers like "1." at the start of a line."""
    text = re.sub(r"(?m)^\s*\d+\s*[.)\-]\s", " ", norm(text))
    return set(re.findall(r"\d+(?:[.,]\d+)?", text))


def ungrounded_numbers(reply, contexts, question):
    """Numbers in the reply that appear in neither the retrieved contexts nor the question."""
    allowed = _numbers(question)
    for c in contexts:
        allowed |= _numbers(c)
    words = norm(question + " " + " ".join(contexts))
    allowed |= {d for w, ds in NUMBER_WORDS.items() if norm(w) in words for d in ds}  # "السادسة عشر" -> 16
    return _numbers(reply) - allowed


def run(data, chunks, vectors, out):
    try:  # warm-up: an empty prompt just loads the model
        _post("/api/generate", {"model": MODEL, "prompt": "", "keep_alive": "30m"})
    except Exception as exc:
        print(f"warning: model warm-up failed ({exc})", file=sys.stderr)
    for msgs in _chat_messages(data):
        history, last, last_fields = [], None, None  # per-chat state only
        for msg in msgs:
            t0, p = time.time(), {"mode": "error", "services": [], "fields": []}
            try:
                q = msg.get("question")  # read once
                if isinstance(q, str) and q.strip():
                    p = plan(q, last, chunks, vectors, last_fields)
                    last = p["pairs"] or last
                    last_fields = p["fields"] or last_fields
                    reply = ask(build_messages(p, q, history))
                    if p["mode"] == "answer" and (not reply or ungrounded_numbers(reply, p["contexts"], q)):
                        # empty, or quotes a number found in neither the documents nor the question: retry plain
                        strict = build_messages(p, q, history)
                        last_user = max(i for i, m in enumerate(strict) if m["role"] == "user")
                        strict[last_user] = dict(strict[last_user], content=strict[last_user]["content"]
                                                 + "\n(استخدم فقط الأرقام الواردة في نتائج البحث كما هي.)")
                        retry = ask(strict) or ask(build_messages(p, q, history, grounded=False))
                        if retry and (not reply or len(ungrounded_numbers(retry, p["contexts"], q))
                                      < len(ungrounded_numbers(reply, p["contexts"], q))):
                            reply = retry
                    elif p["mode"] != "answer" and reply and ungrounded_numbers(reply, [], q):
                        retry = ask(build_messages(p, q, history))  # refusals/clarifications must not invent numbers
                        reply = retry if retry and not ungrounded_numbers(retry, [], q) else reply
                    if not reply:
                        raise RuntimeError("empty reply")
                    msg["answer"], msg["contexts"] = reply, used_contexts(p["contexts"], reply)
                else:  # missing or empty question
                    msg["answer"], msg["contexts"] = "error", []
                sim = f" best_sim={p['best_sim']:.3f}" if p.get("best_sim") is not None else ""
                print(f"{msg.get('message_id', '?')}: mode={p['mode']} services={p['services']} "
                      f"fields={p['fields']}{sim} {time.time() - t0:.1f}s", file=sys.stderr)
                if msg["answer"] != "error":  # failed turns stay out of the history
                    history.append((q, msg["answer"]))
            except Exception:
                traceback.print_exc()
                msg["answer"], msg["contexts"] = "error", []
        save(out, data)  # partial runs still leave output


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="backslashreplace")
        except AttributeError:  # not a TextIOWrapper
            pass
    qpath = sys.argv[1] if len(sys.argv) > 1 else "questions.json"
    try:
        with open(qpath, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"error: cannot load {qpath}: {exc}", file=sys.stderr)
        sys.exit(1)
    out = HERE / "answers.json"
    try:
        chunks = load_chunks(HERE / "data")
        print(f"indexed {len(chunks)} chunks", file=sys.stderr)
        for msgs in _chat_messages(data):  # anything run() does not reach stays marked as failed
            for msg in msgs:
                msg.setdefault("answer", "error")
        run(data, chunks, build_vectors(chunks), out)
    finally:  # fatal errors still leave a complete output file
        for msgs in _chat_messages(data):
            for msg in msgs:
                msg.setdefault("answer", "error")
                msg.setdefault("contexts", [])
        save(out, data)
    print(f"wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
