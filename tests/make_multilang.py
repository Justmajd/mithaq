"""Build 4 parallel test sets (70 messages each): Arabic, English, mixed Arabic/English, Arabizi.

The same 70 facts/scenarios are phrased in each language, so scores are comparable across languages.
Run: python3 tests/make_multilang.py  -> tests/q_ar.json, q_en.json, q_mx.json, q_az.json
"""
import json
from pathlib import Path

S = {  # service keys -> exact service names used in contexts
    "P1": "جواز سفر لأول مرة", "P2": "تجديد جواز السفر", "P3": "جواز سفر بدل فاقد", "P4": "جواز سفر بدل تالف",
    "F1": "دفتر عائلة لأول مرة", "F2": "تجديد دفتر العائلة", "F3": "دفتر عائلة بدل فاقد", "F4": "دفتر عائلة بدل تالف",
    "I1": "البطاقة الذكية لأول مرة", "I2": "تجديد البطاقة الذكية", "I3": "البطاقة الذكية بدل فاقد",
    "I4": "البطاقة الذكية بدل تالف",
}
N1 = ["1", "واحده", "one", "single"]
N2 = ["2", "دينارين", "ديناران", "two", "اثنين", "صورتين", "صورتان"]
N3 = ["3", "ثلاث", "three"]
N5 = ["5", "خمس", "five"]
N10 = ["10", "عشر", "ten"]
N20 = ["20", "عشرين", "twenty"]

# (type, must, ctx) for the 40 factual questions, in order
FACTS = [
    ("fee_situation", [["50"]], ["P2"]),                     # 1 renew passport, adult, expired
    ("fee_situation", [["25"]], ["P2"]),                     # 2 renew passport, under 16
    ("fee_situation", [["100"]], ["P2"]),                    # 3 renew passport, living abroad
    ("fee_situation", [N20], ["P2"]),                        # 4 renew passport, full pages still valid
    ("hidden_in_notes", [["25"]], ["P2"]),                   # 5 urgent office extra
    ("time", [["45"]], ["P2"]),                              # 6 renewal time
    ("documents", [N2], ["P2"]),                             # 7 photos for renewal
    ("fee_situation", [["50"]], ["P1"]),                     # 8 first passport, adult in Jordan
    ("fee_situation", [["100"]], ["P1"]),                    # 9 first passport, abroad
    ("fee_situation", [["25"]], ["P1"]),                     # 10 first passport, child
    ("places", [["مكاتب", "office", "مكتب"]], ["P1"]),       # 11 where to apply first passport
    ("fee", [N3], ["I4"]),                                   # 12 damaged ID fee
    ("fee_situation", [["125"]], ["P3"]),                    # 13 lost passport first time
    ("fee_situation", [["250"]], ["P3"]),                    # 14 lost passport second time
    ("documents", [["بلاغ", "report", "police", "شرطه", "مركز الامني", "المركز الامني"]], ["P3"]),  # 15
    ("documents", [["50"], ["500"]], ["P3"]),                # 16 guarantee range
    ("fee", [["100"]], ["P4"]),                              # 17 damaged passport fee
    ("hidden_in_notes", [["لجنه التحقيق", "investigation"]], ["P4"]),  # 18 intentional damage
    ("documents", [N2], ["P4"]),                             # 19 photos damaged passport
    ("fee", [N2], ["F1"]),                                   # 20 first family book fee
    ("fee_situation", [N10], ["F1"]),                        # 21 late after 90 days
    ("documents", [["شهاده الزواج", "عقد الزواج", "marriage certificate", "marriage contract"]], ["F1"]),  # 22
    ("time", [["45"]], ["F1"]),                              # 23 first family book time
    ("fee_situation", [N2], ["F2"]),                         # 24 renew expired family book
    ("fee_situation", [N3], ["F2"]),                         # 25 renew non-expired family book
    ("hidden_in_notes", [["ثلاثه اشهر", "3 اشهر", "three months", "3 months", "ثلاث اشهر"]], ["F2"]),  # 26
    ("places", [["سفار", "embass", "قنصل", "consul"]], ["F2"]),  # 27 renew family book abroad
    ("fee", [N5], ["F3"]),                                   # 28 lost family book fee
    ("conditions", [["رب الاسره", "head of"], ["الزوجه", "wife", "spouse", "زوجه"]], ["F3"]),  # 29 who applies
    ("hidden_in_notes", [["50", "خمسين", "fifty"]], ["F3"]),  # 30 third loss
    ("fee", [N3], ["F4"]),                                   # 31 damaged family book fee
    ("documents", [N10], ["F4"]),                            # 32 pledge value
    ("fee", [N2], ["I1"]),                                   # 33 first ID fee
    ("hidden_in_notes", [N10], ["I1"]),                      # 34 late fine 18+
    ("documents", [N1], ["I1"]),                             # 35 photos first ID
    ("documents", [["زمره الدم", "blood", "الفحص الطبي"]], ["I1"]),  # 36 blood type
    ("fee", [N2], ["I2"]),                                   # 37 renew ID fee
    ("time", [N20], ["I2"]),                                 # 38 renew ID time
    ("fee", [N5], ["I3"]),                                   # 39 lost ID fee
    ("hidden_in_notes", [["اسبوعين", "two weeks", "2 weeks", "14"]], ["I3"]),  # 40 when card is issued
]
COMPARISONS = [
    ([["45"], N20], ["P2", "I2"]),
    ([N5], ["F3", "I3"]),
    ([["100"], N3], ["P4", "I4"]),
    ([N2, N1], ["P1", "I1"]),
    ([N2], ["F2", "I2"]),
    ([["125"], N5], ["P3", "F3"]),
]
WRONG = [
    ([["دون موافقه", "بدون موافقه", "without", "doesn't need", "does not need", "no need", "not need",
       "لا تحتاج", "لا يشترط", "لا يلزم", "يحق", "not required", "can get"]], ["P1"]),
    ([["مكاتب", "مكتب", "office"]], ["I2"]),
    ([["45"]], ["F2"]),
    ([N2], ["I2"]),
    ([["100"]], ["P4"]),
    ([["ولي الامر", "guardian", "لا يقبل", "not accepted", "proxy", "power of attorney", "توكيل", "تفويض"]], ["I3"]),
]
CONV = [  # (must, ctx) for each turn
    [([], ["F3"]), ([N5], ["F3"])],
    [([], ["P1"]), ([["25"]], ["P1"])],
    [([], "empty"), ([N3], ["I4"])],
]

Q = {}  # language -> dict(facts=[40], comp=[6], wrong=[6], unclear=[5], oos=[7], conv=[[2],[2],[2]])

Q["ar"] = dict(
    facts=[
        "عمري 35 وجوازي منتهي من شهرين، قديش رسوم التجديد؟",
        "ابني عمره 13 سنة وجوازه انتهى، كم رسوم تجديده؟",
        "أنا مقيم بالإمارات وبدي أجدد جواز سفري من هناك، كم الرسوم؟",
        "جواز سفري لسا ساري بس الصفحات كلها امتلت، كم بكلف تجديده؟",
        "إذا جددت الجواز بمكتب الخدمة المستعجلة، في مبلغ زيادة؟",
        "كم دقيقة بياخذ تجديد جواز السفر؟",
        "كم صورة شخصية لازم أجيب لتجديد الجواز؟",
        "عمري 22 وساكن بالزرقاء، قديش بدفع لأول جواز سفر إلي؟",
        "أنا أردني مقيم بقطر وما عمري طلعت جواز، كم رسوم أول جواز من السفارة؟",
        "بنتي عمرها 8 سنين بدي أطلعلها أول جواز سفر، كم الرسوم؟",
        "وين بقدم على جواز سفر لأول مرة؟",
        "بطاقتي الذكية انكسرت نصين، قديش رسوم بدل التالف؟",
        "أول مرة بضيع جوازي، كم بدفع عشان أطلع بدل فاقد؟",
        "هاي تاني مرة بضيع فيها جواز السفر، قديش الرسوم هالمرة؟",
        "شو الأوراق المطلوبة لجواز سفر بدل فاقد؟ بدي بلاغ من الشرطة؟",
        "سمعت إنه في كفالة مالية لجواز بدل فاقد، قديش قيمتها؟",
        "جوازي وقعت عليه قهوة وتلف، كم رسوم بدل التالف؟",
        "إذا الجواز تلف بشكل متعمد شو بصير بالمعاملة؟",
        "كم صورة بحتاج لجواز سفر بدل تالف؟",
        "قديش رسوم إصدار دفتر العائلة لأول مرة؟",
        "صارلي 5 شهور متزوج وما طلعت دفتر عائلة، في غرامة؟ قديش؟",
        "شو الوثائق المطلوبة لأول دفتر عائلة بعد الزواج؟",
        "كم بياخذ وقت إصدار دفتر عائلة لأول مرة؟",
        "دفتر العيلة تبعي منتهي، قديش رسوم تجديده؟",
        "بدي أجدد دفتر العائلة مع إنه لسا ما انتهى، كم الرسوم؟",
        "انتهت صلاحية دفتر العائلة، خلال قديش لازم أجدده؟",
        "أنا عايش بكندا، بقدر أجدد دفتر العائلة من السفارة الأردنية؟",
        "ضاع دفتر العائلة، كم رسوم بدل الفاقد؟",
        "مين المسموح له يقدم طلب دفتر عائلة بدل فاقد؟",
        "هاي تالت مرة بضيع دفتر العائلة، شو المبلغ اللي بفرضوه؟",
        "دفتر العائلة اتمزق، قديش بدفع لبدل التالف؟",
        "قديش قيمة التعهد الخطي لدفتر العائلة بدل تالف؟",
        "قديش رسوم البطاقة الذكية لأول مرة؟",
        "عمري 20 وما طلعت هوية أبداً، في غرامة تأخير لما أطلعها لأول مرة؟",
        "كم صورة بدها البطاقة الذكية لأول مرة؟",
        "لازم أعمل فحص زمرة دم عشان أطلع هوية لأول مرة؟",
        "كم بتكلف تجديد البطاقة الذكية؟",
        "قديش بياخذ وقت تجديد الهوية؟",
        "ضاعت بطاقتي الذكية، كم رسوم البدل فاقد؟",
        "بلغت الشرطة إنه هويتي ضاعت، إمتى بقدر أستلم البطاقة البديلة؟",
    ],
    comp=[
        "أيهما أسرع: تجديد جواز السفر أم تجديد البطاقة الذكية؟",
        "قارن لي رسوم دفتر العائلة بدل فاقد مع رسوم البطاقة الذكية بدل فاقد.",
        "شو الفرق بالرسوم بين جواز بدل تالف وهوية بدل تالف؟",
        "كم صورة بحتاج لجواز سفر أول مرة وكم صورة للبطاقة الذكية أول مرة؟",
        "قديش رسوم تجديد دفتر العائلة المنتهي وقديش رسوم تجديد الهوية؟",
        "ضاع جوازي لأول مرة وضاع دفتر العيلة كمان، قديش رسوم كل واحد؟",
    ],
    wrong=[
        "أنا متزوجة، صح لازم زوجي يوافق عشان أطلع جواز سفر لأول مرة؟",
        "بدي أجدد هويتي من السفارة الأردنية بلندن، شو بلزمني؟",
        "تجديد دفتر العائلة بياخذ يومين صح؟",
        "تجديد البطاقة الذكية مجاني صح؟",
        "رسوم جواز السفر بدل تالف 20 دينار بس صح؟",
        "ابن أختي عمره 15 وضاعت هويته، بقدر أنا أقدم عنه بوكالة؟",
    ],
    unclear=[
        "قديش الرسوم؟",
        "شو الأوراق اللي بلزمني؟",
        "كم بياخذ وقت؟",
        "بدي أعمل تجديد",
        "ضاع مني، شو أعمل؟",
    ],
    oos=[
        "كم رسوم تجديد رخصة القيادة؟",
        "بدي فيزا لألمانيا، شو المطلوب؟",
        "كيف بطلع شهادة ميلاد لابني الجديد؟",
        "إيمتى بيفتح مكتب الأحوال يوم الجمعة؟",
        "كم رسوم تصديق شهادة الجامعة؟",
        "كم سعر تذكرة الطيارة من عمان لإسطنبول؟",
        "وين أطيب منسف بإربد؟",
    ],
    conv=[
        ["ضاع دفتر العائلة تبعنا امبارح", "وقديش بدفع؟"],
        ["بدي أطلع جواز سفر لأول مرة لبنتي عمرها 10 سنين", "كم الرسوم إلها؟"],
        ["عندي سؤال عن البطاقة الذكية", "بدل تالف، قديش الرسوم؟"],
    ],
)

Q["en"] = dict(
    facts=[
        "I'm 35 and my passport expired two months ago. How much is the renewal fee?",
        "My son is 13 and his passport expired, how much does renewing it cost?",
        "I live in the UAE and want to renew my Jordanian passport from there. What's the fee?",
        "My passport is still valid but all the pages are full. How much to renew it?",
        "Is there an extra charge if I renew my passport at the urgent service office?",
        "How many minutes does a passport renewal take?",
        "How many personal photos do I need to bring to renew my passport?",
        "I'm 22 and live in Zarqa. How much do I pay for my first passport?",
        "I'm Jordanian living in Qatar and never had a passport. What is the fee for a first-time passport abroad?",
        "My daughter is 8 and I want to get her first passport. What are the fees?",
        "Where can I apply for a passport for the first time?",
        "My smart ID card snapped in half. How much is the replacement for a damaged card?",
        "I lost my passport for the first time ever. How much is a lost passport replacement?",
        "This is the second time I've lost my passport. How much will it cost this time?",
        "What documents do I need for a lost passport replacement? Do I need a police report?",
        "I heard there's a financial guarantee for a lost passport. How much is it?",
        "I spilled coffee on my passport and it's damaged. What's the fee for a damaged passport?",
        "What happens if a passport was damaged on purpose?",
        "How many photos are required for a damaged passport replacement?",
        "How much does it cost to issue a family book for the first time?",
        "I've been married 5 months and never got a family book. Is there a fine for the first one? How much?",
        "What documents are required for a first family book after marriage?",
        "How long does it take to get a family book for the first time?",
        "My family book has expired. How much is the renewal?",
        "I want to renew my family book even though it hasn't expired yet. What's the fee?",
        "My family book expired. Within how long do I have to renew it?",
        "I live in Canada. Can I renew my family book at the Jordanian embassy?",
        "We lost our family book. What is the fee for a lost family book?",
        "Who is allowed to apply for a lost family book replacement?",
        "This is the third time we've lost the family book. What amount do they charge?",
        "Our family book got torn. How much do I pay for a damaged family book replacement?",
        "What is the value of the written pledge for a damaged family book?",
        "How much is the smart ID card for the first time?",
        "I'm 20 and never got an ID card. Is there a late fine when I get it for the first time?",
        "How many photos does a first-time smart ID card need?",
        "Do I need a blood type test to get my ID card for the first time?",
        "How much does it cost to renew the smart ID card?",
        "How long does an ID card renewal take?",
        "I lost my smart ID card. What's the fee for a replacement?",
        "I reported my lost ID to the police. When can I collect the replacement card?",
    ],
    comp=[
        "Which is faster: renewing a passport or renewing the smart ID card?",
        "Compare the fee for a lost family book with the fee for a lost smart ID card.",
        "What's the difference in fees between a damaged passport and a damaged ID card?",
        "How many photos for a first-time passport and how many for a first-time smart ID card?",
        "How much is renewing an expired family book, and how much is renewing the ID card?",
        "I lost my passport for the first time and also lost the family book. How much is each?",
    ],
    wrong=[
        "I'm a married woman. I need my husband's approval to get my first passport, right?",
        "I want to renew my ID card at the Jordanian embassy in London. What do I need?",
        "Renewing the family book takes two days, right?",
        "Renewing the smart ID card is free, isn't it?",
        "A damaged passport replacement is only 20 JD, correct?",
        "My nephew is 15 and lost his ID card. Can I apply for him with a power of attorney?",
    ],
    unclear=[
        "How much are the fees?",
        "What papers do I need?",
        "How long does it take?",
        "I want to renew.",
        "I lost it, what should I do?",
    ],
    oos=[
        "How much is a driving license renewal?",
        "I need a visa to Germany, what is required?",
        "How do I get a birth certificate for my newborn?",
        "What time does the civil status office open on Friday?",
        "How much does it cost to attest a university degree?",
        "How much is a flight ticket from Amman to Istanbul?",
        "Where is the best mansaf restaurant in Irbid?",
    ],
    conv=[
        ["We lost our family book yesterday.", "And how much do I pay?"],
        ["I want to get a passport for the first time for my daughter, she's 10.", "How much is the fee for her?"],
        ["I have a question about the smart ID card.", "It's damaged, how much is the fee?"],
    ],
)

Q["mx"] = dict(
    facts=[
        "عمري 35 والـ passport تبعي expired من شهرين، قديش الـ renewal fee؟",
        "ابني عمره 13 وجوازه expired، how much تجديده؟",
        "I live in الإمارات وبدي أجدد الجواز من هناك، شو الـ fees؟",
        "الـ passport لسا valid بس الصفحات full، كم بكلف الـ renewal؟",
        "إذا جددت الجواز بالـ urgent office، في extra charge؟",
        "how many minutes بياخذ تجديد جواز السفر؟",
        "كم personal photo لازم أجيب لـ renew الجواز؟",
        "عمري 22 وساكن بالزرقاء، how much بدفع لأول passport؟",
        "أنا أردني living in Qatar وما عمري طلعت جواز، كم الـ fee لأول جواز من السفارة؟",
        "بنتي عمرها 8 وبدي أطلعلها first passport، كم الرسوم؟",
        "where بقدر أقدم على جواز سفر لأول مرة؟",
        "الـ smart card تبعتي انكسرت، قديش fee بدل التالف؟",
        "first time بضيع الـ passport، كم بدفع لبدل فاقد؟",
        "هاي second time بضيع فيها الجواز، how much هالمرة؟",
        "شو الـ documents المطلوبة لجواز بدل فاقد؟ بحتاج police report؟",
        "سمعت في financial guarantee لجواز بدل فاقد، قديش قيمتها؟",
        "وقعت قهوة على الـ passport وصار damaged، كم رسوم بدل التالف؟",
        "if الجواز تلف on purpose شو بصير؟",
        "how many photos بحتاج لجواز بدل تالف؟",
        "قديش fee دفتر العائلة for the first time؟",
        "متزوج من 5 months وما طلعت family book، في غرامة؟ how much؟",
        "شو الـ documents المطلوبة لأول دفتر عائلة بعد الزواج؟",
        "how long بياخذ إصدار دفتر عائلة لأول مرة؟",
        "الـ family book تبعي expired، قديش الـ renewal؟",
        "بدي renew دفتر العائلة مع إنه not expired، كم الرسوم؟",
        "دفتر العائلة expired، within how long لازم أجدده؟",
        "I live in Canada، بقدر أجدد دفتر العائلة من الـ embassy؟",
        "ضاع الـ family book، كم الـ fee لبدل فاقد؟",
        "who مسموح له يقدم على دفتر عائلة بدل فاقد؟",
        "third time بنضيع دفتر العائلة، شو الـ amount اللي بفرضوه؟",
        "دفتر العائلة torn، قديش بدفع لـ damaged replacement؟",
        "قديش قيمة الـ written pledge لدفتر عائلة بدل تالف؟",
        "how much البطاقة الذكية for the first time؟",
        "عمري 20 وما عمري طلعت ID، في late fine لما أطلعها أول مرة؟",
        "كم photo بدها الـ smart ID أول مرة؟",
        "لازم blood type test عشان أطلع هوية لأول مرة؟",
        "how much تجديد البطاقة الذكية؟",
        "قديش بياخذ time تجديد الـ ID؟",
        "ضاعت الـ smart card تبعتي، كم fee البدل فاقد؟",
        "بلغت الـ police إنه هويتي ضاعت، when بقدر أستلم البطاقة الجديدة؟",
    ],
    comp=[
        "which is faster: تجديد الجواز ولا تجديد الهوية؟",
        "compare رسوم دفتر العائلة بدل فاقد مع fee البطاقة الذكية بدل فاقد",
        "شو الـ difference بالرسوم بين damaged passport وهوية بدل تالف؟",
        "كم photo لـ first passport وكم لـ first smart ID؟",
        "how much تجديد دفتر العائلة expired وكم تجديد الهوية؟",
        "ضاع الـ passport أول مرة وضاع الـ family book كمان، how much كل واحد؟",
    ],
    wrong=[
        "أنا married، صح لازم husband approval عشان أطلع جواز لأول مرة؟",
        "بدي renew هويتي من السفارة الأردنية in London، شو بلزمني؟",
        "تجديد دفتر العائلة takes two days صح؟",
        "تجديد البطاقة الذكية free صح؟",
        "damaged passport replacement بس 20 دينار صح؟",
        "ابن أختي 15 years وضاعت هويته، بقدر أقدم عنه with power of attorney؟",
    ],
    unclear=[
        "how much الرسوم؟",
        "شو الـ papers اللي بلزمني؟",
        "how long بياخذ؟",
        "بدي أعمل renewal",
        "ضاع مني، what should I do؟",
    ],
    oos=[
        "how much تجديد رخصة القيادة؟",
        "بدي visa لألمانيا، شو المطلوب؟",
        "كيف بطلع birth certificate لابني؟",
        "what time بيفتح مكتب الأحوال يوم الجمعة؟",
        "كم رسوم attestation شهادة الجامعة؟",
        "how much تذكرة الطيارة من عمان لإسطنبول؟",
        "وين best منسف بإربد؟",
    ],
    conv=[
        ["we lost دفتر العائلة امبارح", "وقديش بدفع؟"],
        ["بدي أطلع first passport لبنتي عمرها 10", "how much الرسوم إلها؟"],
        ["عندي question عن البطاقة الذكية", "damaged، قديش الـ fee؟"],
    ],
)

Q["az"] = dict(
    facts=[
        "3omri 35 w el jawaz tabi3i montahi mn shahren, 2adesh rsoom el tajdeed?",
        "ibni 3omro 13 w jawazo montahi, kam rsoom tajdeedo?",
        "ana sakin bl emarat w bdi ajadded el jawaz mn hnak, 2adesh el rsoom?",
        "el jawaz lissa sari bs el sf7at kollha mtalat, 2adesh bkalef tajdeedo?",
        "iza jadadt el jawaz b maktab el 5edme el mista3jle, fi mablagh zyade?",
        "kam da2i2a byakhod tajdeed el jawaz?",
        "kam sora shakhsiye lazem ajeeb la tajdeed el jawaz?",
        "3omri 22 w sakin bl zar2a, 2adesh badfa3 la awal jawaz ili?",
        "ana ordoni 3ayesh b 2a6ar w ma 3omri 6ala3t jawaz, kam rsoom awal marra jawaz mn el safara?",
        "binti 3omraha 8 sneen bdi a6la3laha jawaz awal marra, kam el rsoom?",
        "wen b2adem 3ala jawaz safar awal marra?",
        "el beta2a el thakiye tab3ti inkasarat, 2adesh rsoom bdal talef?",
        "awal marra bdayya3 jawazi, kam badfa3 3shan a6la3 bdal fa2ed?",
        "hay tani marra bdayya3 el basbor, 2adesh el rsoom hal marra?",
        "shu el awra2 el ma6looba la jawaz bdal fa2ed? b7taj balagh mn el shor6a?",
        "sme3t fi kafale maliye la jawaz bdal fa2ed, 2adesh 2eemet-ha?",
        "w2e3 2ahwe 3al jawaz w sar talef, kam rsoom bdal el talef?",
        "iza el jawaz tilef 3an 2asd shu bseer?",
        "kam sora b7taj la jawaz bdal talef?",
        "2adesh rsoom daftar el 3ayle awal marra?",
        "sarli 5 shhoor mitjawwez w ma 6ala3t daftar 3ayle, fi 8arame? 2adesh?",
        "shu el wathayi2 el ma6looba la awal daftar 3ayle ba3d el zawaj?",
        "kam byakhod wa2t isdar daftar 3ayle awal marra?",
        "daftar el 3ayle tab3i montahi, 2adesh rsoom tajdeedo?",
        "bdi ajadded daftar el 3ayle ma3 enno lissa mish montahi, kam el rsoom?",
        "daftar el 3ayle intaha, 5ilal 2adesh lazem ajaddedo?",
        "ana 3ayesh b canada, b2dar ajadded daftar el 3ayle mn el safara el ordoniye?",
        "da3 daftar el 3ayle, kam rsoom bdal fa2ed?",
        "meen msmoo7lo y2adem 6alab daftar 3ayle bdal fa2ed?",
        "hay talet marra bndayya3 daftar el 3ayle, shu el mablagh elli bfrdoo?",
        "daftar el 3ayle tmazza2, 2adesh badfa3 la bdal talef?",
        "2adesh 2eemet el ta3ahhod el 5a66i la daftar 3ayle bdal talef?",
        "2adesh rsoom el beta2a el thakiye awal marra?",
        "3omri 20 w ma 3omri 6ala3t hawiye, fi 8aramet ta25eer lama a6la3ha awal marra?",
        "kam sora bad-ha el beta2a el thakiye awal marra?",
        "lazem a3mal fa7s zomret dam 3shan a6la3 hawiye awal marra?",
        "kam btkalef tajdeed el beta2a el thakiye?",
        "2adesh byakhod wa2t tajdeed el hawiye?",
        "da3at beta2ti el thakiye, kam rsoom el bdal fa2ed?",
        "ballaght el shor6a enno hawiyti da3at, emta b2dar astalem el beta2a el jdeede?",
    ],
    comp=[
        "ayy wa7ad asra3: tajdeed el jawaz walla tajdeed el hawiye?",
        "2arenli rsoom daftar el 3ayle bdal fa2ed ma3 rsoom el beta2a el thakiye bdal fa2ed",
        "shu el far2 bl rsoom bain jawaz bdal talef w hawiye bdal talef?",
        "kam sora b7taj la jawaz awal marra w kam sora lal beta2a el thakiye awal marra?",
        "2adesh rsoom tajdeed daftar el 3ayle el montahi w 2adesh tajdeed el hawiye?",
        "da3 jawazi awal marra w da3 daftar el 3ayle kaman, 2adesh rsoom kol wa7ad?",
    ],
    wrong=[
        "ana mitjawwze, sa7 lazem jozi ywaf2 3shan a6la3 jawaz awal marra?",
        "bdi ajadded hawiyti mn el safara el ordoniye b london, shu blzamni?",
        "tajdeed daftar el 3ayle byakhod yomen sa7?",
        "tajdeed el beta2a el thakiye majjani sa7?",
        "rsoom jawaz bdal talef 20 dinar bs sa7?",
        "ibn o5ti 3omro 15 w da3at hawiyto, b2dar ana a2adem 3anno b wakale?",
    ],
    unclear=[
        "2adesh el rsoom?",
        "shu el awra2 elli blzamni?",
        "kam byakhod wa2t?",
        "bdi a3mal tajdeed",
        "da3 mni, shu a3mal?",
    ],
    oos=[
        "kam rsoom tajdeed ro5set el swa2a?",
        "bdi fiza la almanya, shu el ma6loob?",
        "kif ba6la3 shahadet milad la ibni?",
        "emta byefta7 maktab el a7wal yom el jom3a?",
        "kam rsoom tasdee2 shahadet el jam3a?",
        "kam se3r tathkaret el tayyara mn 3amman la istanbul?",
        "wen a6yab mansaf b irbid?",
    ],
    conv=[
        ["da3 daftar el 3ayle tab3na mbare7", "w 2adesh badfa3?"],
        ["bdi a6la3 jawaz awal marra la binti 3omraha 10", "kam el rsoom ilha?"],
        ["3indi so2al 3an el beta2a el thakiye", "bdal talef, 2adesh el rsoom?"],
    ],
)


def ctx(keys):
    return "empty" if keys == "empty" else [S[k] for k in keys]


def build(lang):
    q, chats, n = Q[lang], [], 0

    def add(type_, question, must, keys):
        nonlocal n
        n += 1
        cid = f"{lang}-c{n:02d}"
        chats.append({"chat_id": cid, "messages": [
            {"message_id": f"{cid}-1", "type": type_, "question": question, "must": must, "ctx": ctx(keys)}]})

    assert len(q["facts"]) == len(FACTS) == 40
    for text, (t, must, keys) in zip(q["facts"], FACTS):
        add(t, text, must, keys)
    for text, (must, keys) in zip(q["comp"], COMPARISONS):
        add("comparison", text, must, keys)
    for text, (must, keys) in zip(q["wrong"], WRONG):
        add("wrong_assumption", text, must, keys)
    for text in q["unclear"]:
        add("unclear", text, [], "empty")
    for text in q["oos"]:
        add("out_of_scope", text, [], "empty")
    for turns, specs in zip(q["conv"], CONV):
        n += 1
        cid = f"{lang}-c{n:02d}"
        chats.append({"chat_id": cid, "messages": [
            {"message_id": f"{cid}-{i + 1}", "type": "conversation", "question": t, "must": m, "ctx": ctx(k)}
            for i, (t, (m, k)) in enumerate(zip(turns, specs))]})
    total = sum(len(c["messages"]) for c in chats)
    assert total == 70, (lang, total)
    return {"chats": chats}


if __name__ == "__main__":
    out = Path(__file__).resolve().parent
    for lang in Q:
        (out / f"q_{lang}.json").write_text(json.dumps(build(lang), ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"q_{lang}.json: 70 messages")
