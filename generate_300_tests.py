"""
Generates 3 comprehensive, high-coverage test suites (100 Fusha, 100 Ammiya, 100 English = 300 tests)
for the 42 Irbid AI Hackathon Civil Status & Passports RAG system.
"""

import json
import os

def create_fusha_chats():
    chats = []
    # 25 chats, 4 msgs each = 100 questions
    
    # Chat 1: Passport First Issue & Minor Rules
    chats.append({
        "chat_id": "fusha_chat_01",
        "messages": [
            {"message_id": "fusha_01_01", "question": "ما هي الوثائق المطلوبة لإصدار جواز سفر عادي لأول مرة لمن أتم 16 سنة من عمره؟"},
            {"message_id": "fusha_01_02", "question": "وكم تبلغ الرسوم القانونية المقررة لهذه الفئة العمرية؟"},
            {"message_id": "fusha_01_03", "question": "وما هي الرسوم إذا كان عمر المتقدم دون سن 16 عاماً؟"},
            {"message_id": "fusha_01_04", "question": "هل يشترط موافقة خطية من ولي الأمر لمن هم دون سن 18 عاماً؟"}
        ]
    })
    
    # Chat 2: Passport Renewal & Locations
    chats.append({
        "chat_id": "fusha_chat_02",
        "messages": [
            {"message_id": "fusha_02_01", "question": "كم تبلغ رسوم تجديد جواز السفر العادي منتهي الصلاحية داخل المملكة؟"},
            {"message_id": "fusha_02_02", "question": "وإذا كان الجواز ممتلئ الصفحات قبل انتهاء مدته، كم تكون الرسوم؟"},
            {"message_id": "fusha_02_03", "question": "أين يمكن للمواطن المقيم خارج الأردن تقديم طلب التجديد؟"},
            {"message_id": "fusha_02_04", "question": "ما هو الزمن المستغرق لإنجاز معاملة تجديد الجواز في مكاتب الأحوال؟"}
        ]
    })

    # Chat 3: Passport Lost & Damaged Comparison
    chats.append({
        "chat_id": "fusha_chat_03",
        "messages": [
            {"message_id": "fusha_03_01", "question": "كم رسم إصدار جواز سفر بدل فاقد لأول مرة؟"},
            {"message_id": "fusha_03_02", "question": "وكم تبلغ الرسوم إذا فُقد الجواز للمرة الثانية أو أكثر؟"},
            {"message_id": "fusha_03_03", "question": "كم تبلغ رسوم إصدار جواز سفر بدل تالف؟"},
            {"message_id": "fusha_03_04", "question": "أيهما أعلى رسوماً: إصدار جواز بدل تالف أم بدل فاقد للمرة الأولى؟"}
        ]
    })

    # Chat 4: Smart ID Card First Issue
    chats.append({
        "chat_id": "fusha_chat_04",
        "messages": [
            {"message_id": "fusha_04_01", "question": "ما هي شروط وإجراءات إصدار البطاقة الشخصية الذكية لأول مرة عند بلوغ سن 16 سنة؟"},
            {"message_id": "fusha_04_02", "question": "ما هي الوثائق المطلوبة لإصدار البطاقة الذكية لأول مرة؟"},
            {"message_id": "fusha_04_03", "question": "كم تبلغ الرسوم المقررة لإصدار البطاقة الذكية لأول مرة؟"},
            {"message_id": "fusha_04_04", "question": "ما هو الزمن المستغرق للحصول على البطاقة الذكية؟"}
        ]
    })

    # Chat 5: Smart ID Renewal & Replacement
    chats.append({
        "chat_id": "fusha_chat_05",
        "messages": [
            {"message_id": "fusha_05_01", "question": "كم تبلغ رسوم تجديد البطاقة الشخصية الذكية بعد انتهاء مدة صلاحيتها؟"},
            {"message_id": "fusha_05_02", "question": "ما هي رسوم إصدار بطاقة ذكية بدل تالف في حال كسرها؟"},
            {"message_id": "fusha_05_03", "question": "وكم تبلغ رسوم إصدار بطاقة ذكية بدل فاقد؟"},
            {"message_id": "fusha_05_04", "question": "ما هي الوثائق المطلوبة في حال التقدم بطلب بطاقة ذكية بدل فاقد؟"}
        ]
    })

    # Chat 6: Family Book First Issue & Wedding Delays
    chats.append({
        "chat_id": "fusha_chat_06",
        "messages": [
            {"message_id": "fusha_06_01", "question": "ما هي الوثائق المطلوبة لإصدار دفتر العائلة لأول مرة بعد الزواج؟"},
            {"message_id": "fusha_06_02", "question": "كم تبلغ رسوم إصدار دفتر العائلة لأول مرة ضمن المدة القانونية؟"},
            {"message_id": "fusha_06_03", "question": "إذا تم تقديم الطلب بعد مرور 4 أشهر على عقد الزواج، فكم تبلغ الرسوم الإجمالية مع الغرامة؟"},
            {"message_id": "fusha_06_04", "question": "ما هو الحد الزمني القانوني المسموح به قبل استحقاق غرامة التأخير؟"}
        ]
    })

    # Chat 7: Family Book Renewal, Lost, & Damaged
    chats.append({
        "chat_id": "fusha_chat_07",
        "messages": [
            {"message_id": "fusha_07_01", "question": "كم تبلغ رسوم تجديد دفتر العائلة في حال امتلائه بأسماء الأبناء؟"},
            {"message_id": "fusha_07_02", "question": "كم رسم إصدار دفتر عائلة بدل فاقد؟"},
            {"message_id": "fusha_07_03", "question": "كم تبلغ رسوم إصدار دفتر عائلة بدل تالف؟"},
            {"message_id": "fusha_07_04", "question": "أيهما أعلى كلفة: دفتر عائلة بدل فاقد أم بدل تالف؟"}
        ]
    })

    # Chat 8: Deceased Parents & Head of Family Rules
    chats.append({
        "chat_id": "fusha_chat_08",
        "messages": [
            {"message_id": "fusha_08_01", "question": "في حال وفاة الوالد، هل يحق للأرملة الحصول على دفتر عائلة باسمها؟"},
            {"message_id": "fusha_08_02", "question": "وإذا توفي الأب والأم معاً، فمن يعتبر رباً للأسرة في دفتر العائلة؟"},
            {"message_id": "fusha_08_03", "question": "ما هي الشروط إذا كان أكبر الأبناء متزوجاً؟"},
            {"message_id": "fusha_08_04", "question": "هل يترتب رسم إصدار على دفتر العائلة في هذه الحالة وكم يبلغ؟"}
        ]
    })

    # Chat 9: False Assumptions Correction
    chats.append({
        "chat_id": "fusha_chat_09",
        "messages": [
            {"message_id": "fusha_09_01", "question": "هل يشترط إحضار موافقة خطية من الزوج لإصدار جواز سفر للزوجة الأردنية؟"},
            {"message_id": "fusha_09_02", "question": "هل يمكن للمواطن الأردني تجديد جواز سفره إذا كان متبقياً في صلاحيته سنتان بدون سبب؟"},
            {"message_id": "fusha_09_03", "question": "هل يشترط تقديم شهادة خلو سوابق عند إصدار البطاقة الذكية لأول مرة؟"},
            {"message_id": "fusha_09_04", "question": "هل يعفى فاقد البطاقة الذكية من دفع الرسوم إذا أحضر بلاغاً أمنياً؟"}
        ]
    })

    # Chat 10: Multi-turn Photo Inquiries
    chats.append({
        "chat_id": "fusha_chat_10",
        "messages": [
            {"message_id": "fusha_10_01", "question": "كم عدد الصور الشخصية المطلوبة لإصدار جواز سفر لأول مرة؟"},
            {"message_id": "fusha_10_02", "question": "وكم صورة شخصية تلزم لتجديد جواز السفر؟"},
            {"message_id": "fusha_10_03", "question": "وكم صورة تلزم لإصدار البطاقة الشخصية الذكية لأول مرة لمن هم دون 18 سنة؟"},
            {"message_id": "fusha_10_04", "question": "هل يلزم إحضار صور شخصية لإصدار دفتر العائلة؟"}
        ]
    })

    # Chat 11: Out of Scope Inquiries (Fusha)
    chats.append({
        "chat_id": "fusha_chat_11",
        "messages": [
            {"message_id": "fusha_11_01", "question": "كيف يمكنني تصديق شهادتي الجامعية من وزارة التعليم العالي والبحث العلمي؟"},
            {"message_id": "fusha_11_02", "question": "ما هي رسوم تجديد رخصة اقتناء المركبات في إدارة ترخيص السواقين والمركبات؟"},
            {"message_id": "fusha_11_03", "question": "كم تبلغ ضريبة المسقفات المترتبة على العقارات السكنية لدى أمانة عمان؟"},
            {"message_id": "fusha_11_04", "question": "ما هي خطوات حجز تذاكر الطيران إلى دبي عبر الملكية الأردنية؟"}
        ]
    })

    # Chat 12: Ambiguous Inquiries (Fusha)
    chats.append({
        "chat_id": "fusha_chat_12",
        "messages": [
            {"message_id": "fusha_12_01", "question": "أرغب في تجديد وثيقتي الرسمية، ما هي المتطلبات والرسوم؟"},
            {"message_id": "fusha_12_02", "question": "لقد فقدت وثيقتي الشخصية، ما هي الإجراءات القانونية المتبعة؟"},
            {"message_id": "fusha_12_03", "question": "كم يستغرق إنجاز المعاملة في المكاتب الحكومية؟"},
            {"message_id": "fusha_12_04", "question": "ما هي الرسوم الإجمالية المترتبة على الإصدار لأول مرة؟"}
        ]
    })

    # Chat 13: Passport Expedited & Validity
    chats.append({
        "chat_id": "fusha_chat_13",
        "messages": [
            {"message_id": "fusha_13_01", "question": "هل تختلف رسوم تجديد جواز السفر إذا كان الجواز ساري المفعول لمدة تزيد عن 180 يوماً؟"},
            {"message_id": "fusha_13_02", "question": "كم تبلغ رسوم التجديد إذا كانت المدة المتبقية في الجواز أكثر من 180 يوماً؟"},
            {"message_id": "fusha_13_03", "question": "كم تبلغ مدة صلاحية جواز السفر الممنوح لمن هم دون سن 16 عاماً؟"},
            {"message_id": "fusha_13_04", "question": "وكم تبلغ مدة صلاحية جواز السفر لمن أتم 16 عاماً؟"}
        ]
    })

    # Chat 14: Family Book Separation (طلاق وترمل)
    chats.append({
        "chat_id": "fusha_chat_14",
        "messages": [
            {"message_id": "fusha_14_01", "question": "ما هي شروط وإجراءات فصل دفتر العائلة للمرأة المطلقة؟"},
            {"message_id": "fusha_14_02", "question": "ما هي الوثائق المطلوبة لفصل دفتر العائلة للمطلقة؟"},
            {"message_id": "fusha_14_03", "question": "هل يجوز للمرأة الأرملة الحصول على دفتر عائلة مستقل؟"},
            {"message_id": "fusha_14_04", "question": "كم تبلغ رسوم فصل أو إصدار دفتر العائلة في هذه الحالة؟"}
        ]
    })

    # Chat 15: Partner Institutions & Approvals
    chats.append({
        "chat_id": "fusha_chat_15",
        "messages": [
            {"message_id": "fusha_15_01", "question": "من هم الشركاء المعنيون بتقديم خدمة إصدار جواز سفر لأول مرة؟"},
            {"message_id": "fusha_15_02", "question": "ما هو دور القيادة العامة للقوات المسلحة أو مكتب خدمة العلم في معاملة الجواز؟"},
            {"message_id": "fusha_15_03", "question": "هل تتطلب معاملة جواز السفر بدل الفاقد موافقة أمنية من مديرية الأمن العام؟"},
            {"message_id": "fusha_15_04", "question": "ما هي الجهة الأمنية الشريكة في إصدار البطاقة الذكية بدل الفاقد؟"}
        ]
    })

    # Chat 16: ID Card Blood Type & Sanad Digital Identity
    chats.append({
        "chat_id": "fusha_chat_16",
        "messages": [
            {"message_id": "fusha_16_01", "question": "هل يطلب فحص أو تقرير زمرة الدم عند إصدار البطاقة الذكية لأول مرة؟"},
            {"message_id": "fusha_16_02", "question": "هل يمكن تثبيت زمرة الدم بالاعتماد على رخصة القيادة القديمة؟"},
            {"message_id": "fusha_16_03", "question": "هل تتضمن البطاقة الذكية شريحة إلكترونية لتفعيل الهوية الرقمية عبر تطبيق سند؟"},
            {"message_id": "fusha_16_04", "question": "كم تبلغ رسوم تفعيل الرقم السري أو الشريحة الذكية للبطاقة؟"}
        ]
    })

    # Chat 17: Multi-turn Embassy & Consular Inquiries
    chats.append({
        "chat_id": "fusha_chat_17",
        "messages": [
            {"message_id": "fusha_17_01", "question": "هل يحق للأردني المقيم في دولة الإمارات العربية المتحدة تجديد جواز سفره عبر السفارة الأردنية في أبوظبي؟"},
            {"message_id": "fusha_17_02", "question": "وهل يمكنه أيضاً إصدار جواز سفر بدل فاقد من السفارة؟"},
            {"message_id": "fusha_17_03", "question": "هل يمكن إصدار أو تجديد البطاقة الذكية من السفارات والقنصليات خارج المملكة؟"},
            {"message_id": "fusha_17_04", "question": "أين يجب على المواطن التقدم بطلب للحصول على البطاقة الذكية حصراً؟"}
        ]
    })

    # Chat 18: Step-by-step Procedures
    chats.append({
        "chat_id": "fusha_chat_18",
        "messages": [
            {"message_id": "fusha_18_01", "question": "ما هي الخطوة الأولى عند الوصول إلى مكتب الأحوال المدنية لإصدار البطاقة الذكية؟"},
            {"message_id": "fusha_18_02", "question": "وما هي إجراءات التقاط الصورة الشخصية والبصمات العشرية؟"},
            {"message_id": "fusha_18_03", "question": "أين يتم تسديد الرسوم القانونية للبطاقة الذكية؟"},
            {"message_id": "fusha_18_04", "question": "من هو الشخص المخول قانوناً باستلام البطاقة الذكية بعد طباعتها؟"}
        ]
    })

    # Chat 19: Late Marriage Registration Calculations
    chats.append({
        "chat_id": "fusha_chat_19",
        "messages": [
            {"message_id": "fusha_19_01", "question": "ما هي المدة المحددة قانوناً لتسجيل واقعة الزواج دون استحقاق غرامة مالية؟"},
            {"message_id": "fusha_19_02", "question": "إذا مضى 100 يوم على عقد القران، كم تبلغ غرامة التأخير المقررة قانوناً؟"},
            {"message_id": "fusha_19_03", "question": "كم يصبح إجمالي المبلغ المطلوب لدفتر العائلة متضمناً الرسم والغرامة؟"},
            {"message_id": "fusha_19_04", "question": "وإذا تم استخراج الدفتر في اليوم الثمانين بعد عقد القران، فهل تترتب أي غرامة؟"}
        ]
    })

    # Chat 20: Damaged Conditions & Definition
    chats.append({
        "chat_id": "fusha_chat_20",
        "messages": [
            {"message_id": "fusha_20_01", "question": "متى يعتبر جواز السفر تالفاً من الناحية القانونية؟"},
            {"message_id": "fusha_20_02", "question": "هل تمزق غلاف الجواز أو تعرضه للماء يوجب استخراج بدل تالف؟"},
            {"message_id": "fusha_20_03", "question": "هل يشترط تسليم الجواز التالف القديم لدائرة الأحوال عند تقديم الطلب؟"},
            {"message_id": "fusha_20_04", "question": "كم تبلغ رسوم إصدار جواز سفر بدل تالف؟"}
        ]
    })

    # Chat 21: Lost ID Security Inquiries
    chats.append({
        "chat_id": "fusha_chat_21",
        "messages": [
            {"message_id": "fusha_21_01", "question": "ما هي الإجراءات المطلوبة فور فقدان البطاقة الشخصية الذكية؟"},
            {"message_id": "fusha_21_02", "question": "هل يلزم تنظيم ضبط شرطة أو بلاغ أمني بفقدان البطاقة الذكية؟"},
            {"message_id": "fusha_21_03", "question": "كم تبلغ رسوم استخراج بطاقة ذكية بدل فاقد؟"},
            {"message_id": "fusha_21_04", "question": "ما هو الزمن المستغرق للحصول على البطاقة البديلة؟"}
        ]
    })

    # Chat 22: Adding Newborns to Family Book
    chats.append({
        "chat_id": "fusha_chat_22",
        "messages": [
            {"message_id": "fusha_22_01", "question": "ما هي الوثائق المطلوبة لإضافة مولود جديد إلى دفتر العائلة؟"},
            {"message_id": "fusha_22_02", "question": "كم تبلغ الرسوم المالية لإضافة مولود جديد وتحديث دفتر العائلة؟"},
            {"message_id": "fusha_22_03", "question": "هل يترتب رسم إصدار جديد إذا كان الدفتر ممتلئاً وتطلب الأمر استبداله؟"},
            {"message_id": "fusha_22_04", "question": "كم تبلغ رسوم تجديد دفتر العائلة في حال امتلائه بالكامل؟"}
        ]
    })

    # Chat 23: Mixed Cross-Service Inquiries
    chats.append({
        "chat_id": "fusha_chat_23",
        "messages": [
            {"message_id": "fusha_23_01", "question": "هل يمكن للمواطن تقديم طلب تجديد جواز السفر وإصدار بطاقة ذكية في المعاملة ذاتها؟"},
            {"message_id": "fusha_23_02", "question": "كم تبلغ الرسوم الكلية لتجديد جواز سفر منتهي وصنع بطاقة ذكية لأول مرة؟"},
            {"message_id": "fusha_23_03", "question": "كم صورة شخصية يجب تجهيزها لتغطية هاتين الخدمتين معاً؟"},
            {"message_id": "fusha_23_04", "question": "ما هو الزمن المستغرق لكل خدمة منهما في المكتب؟"}
        ]
    })

    # Chat 24: Single vs Expatriate Family Book
    chats.append({
        "chat_id": "fusha_chat_24",
        "messages": [
            {"message_id": "fusha_24_01", "question": "هل يمنح دفتر العائلة للأردني العازب المستقل؟"},
            {"message_id": "fusha_24_02", "question": "ما هي الفئات المستفيدة من خدمة إصدار دفتر العائلة؟"},
            {"message_id": "fusha_24_03", "question": "أين توجد المكاتب المركزية والميدانية المعتمدة لدائرة الأحوال المدنية؟"},
            {"message_id": "fusha_24_04", "question": "هل يمكن للأردني بالخارج طلب دفتر عائلة من السفارات؟"}
        ]
    })

    # Chat 25: Verification and Final Checks
    chats.append({
        "chat_id": "fusha_chat_25",
        "messages": [
            {"message_id": "fusha_25_01", "question": "ما هي رسوم إصدار جواز السفر لأول مرة لمواطن يبلغ من العمر 25 عاماً؟"},
            {"message_id": "fusha_25_02", "question": "ما هي رسوم إصدار البطاقة الذكية بدل فاقد للمرة الأولى؟"},
            {"message_id": "fusha_25_03", "question": "ما هي عقوبة التأخر في استخراج دفتر العائلة لأكثر من 90 يوماً؟"},
            {"message_id": "fusha_25_04", "question": "ما هو الرسم الأساسي لإصدار دفتر العائلة لأول مرة؟"}
        ]
    })

    return {"chats": chats}


def create_ammiya_chats():
    chats = []
    # 25 chats, 4 msgs each = 100 questions in Jordanian dialect
    
    # Chat 1: جواز لأول مرة
    chats.append({
        "chat_id": "ammiya_chat_01",
        "messages": [
            {"message_id": "ammiya_01_01", "question": "بدي أطلع جواز سفر لأول مرة، شو الأوراق اللي لازم أجيبها معي؟"},
            {"message_id": "ammiya_01_02", "question": "وقديش بكلفني الرسوم إذا كان عمري فوق الـ 16؟"},
            {"message_id": "ammiya_01_03", "question": "وإذا بدي أطلع لأخوي الصغير عمره 12 سنة كم بدفع عنه؟"},
            {"message_id": "ammiya_01_04", "question": "ولازم أبوي ييجي يوقع موافقة لأنه قاصر؟"}
        ]
    })

    # Chat 2: تجديد الجواز
    chats.append({
        "chat_id": "ammiya_chat_02",
        "messages": [
            {"message_id": "ammiya_02_01", "question": "جوازي منتهي وبدي أجدده، كم الرسوم المطلوبة؟"},
            {"message_id": "ammiya_02_02", "question": "طب إذا الجواز باقي فيه 7 شهور وبدي أجدده هسا عشان السفر كم بياخدوا مني؟"},
            {"message_id": "ammiya_02_03", "question": "وين بقدر أقدم وأجدده؟"},
            {"message_id": "ammiya_02_04", "question": "وقديش بطوّل المعاملة لتخلص وأستلم الجواز؟"}
        ]
    })

    # Chat 3: ضاع باسبوري
    chats.append({
        "chat_id": "ammiya_chat_03",
        "messages": [
            {"message_id": "ammiya_03_01", "question": "ضيعت باسبوري ومش لاقيه بالمرة، شو أسوي وكم بدفع بدل فاقد أول مرة؟"},
            {"message_id": "ammiya_03_02", "question": "طب لو سمح الله ضاع مرة ثانية كم بتصير الرسوم؟"},
            {"message_id": "ammiya_03_03", "question": "وجواز بدل تالف كم رسومه؟"},
            {"message_id": "ammiya_03_04", "question": "مين أغلى التالف ولا الفاقد لأول مرة؟"}
        ]
    })

    # Chat 4: البطاقة الذكية لأول مرة
    chats.append({
        "chat_id": "ammiya_chat_04",
        "messages": [
            {"message_id": "ammiya_04_01", "question": "ابني كمل 16 وبدنا نطلعله أول هوية ذكية، شو بنحتاج أوراق؟"},
            {"message_id": "ammiya_04_02", "question": "كم بدفع رسوم على أول بطاقة ذكية؟"},
            {"message_id": "ammiya_04_03", "question": "قديش صورة شخصية لازم نجيب معنا؟"},
            {"message_id": "ammiya_04_04", "question": "كم دقيقة بتقعد لتطلع البطاقة ونستلمها؟"}
        ]
    })

    # Chat 5: تجديد الهوية والبدل
    chats.append({
        "chat_id": "ammiya_chat_05",
        "messages": [
            {"message_id": "ammiya_05_01", "question": "هويتي الذكية انتهت مدتها، كم بكلفني تجديدها؟"},
            {"message_id": "ammiya_05_02", "question": "هويتي انكسرت بالنص، كم رسم بدل التالف؟"},
            {"message_id": "ammiya_05_03", "question": "وإذا ضاعت مني بالشارع وما لقيتها كم بكلف بدل الفاقد؟"},
            {"message_id": "ammiya_05_04", "question": "شو الأوراق اللي لازم أجيبها للبدل فاقد؟"}
        ]
    })

    # Chat 6: زواج ودفتر عيلة جديد
    chats.append({
        "chat_id": "ammiya_chat_06",
        "messages": [
            {"message_id": "ammiya_06_01", "question": "تزوجت جديد وبدي أطلع دفتر عيلة لأول مرة، شو المطلوب مني؟"},
            {"message_id": "ammiya_06_02", "question": "كم رسوم إصدار دفتر العائلة لأول مرة؟"},
            {"message_id": "ammiya_06_03", "question": "تأخرت 4 شهور بعد العرس وما طلعت الدفتر، كم بدفع كامل مع الغرامة؟"},
            {"message_id": "ammiya_06_04", "question": "قديش المهلة اللي بيعطونا إياها قبل ما تنزل الغرامة؟"}
        ]
    })

    # Chat 7: دفتر عيلة مليان أو ضايع
    chats.append({
        "chat_id": "ammiya_chat_07",
        "messages": [
            {"message_id": "ammiya_07_01", "question": "دفتر العيلة تعبى وما ضل فيه وسع للأولاد، كم بكلف تجديده؟"},
            {"message_id": "ammiya_07_02", "question": "دفتر عيلتنا ضاع، كم بندفع على بدل الفاقد؟"},
            {"message_id": "ammiya_07_03", "question": "وإذا كان مبلول ومفروم ومتقطع كم بدل التالف؟"},
            {"message_id": "ammiya_07_04", "question": "مين بكلف أكثر دفتر فاقد ولا تالف؟"}
        ]
    })

    # Chat 8: وفاة الأب ورب الأسرة
    chats.append({
        "chat_id": "ammiya_chat_08",
        "messages": [
            {"message_id": "ammiya_08_01", "question": "أبونا توفى الله يرحمه، أمي بتقدر تطلع دفتر عيلة باسمها؟"},
            {"message_id": "ammiya_08_02", "question": "وإذا الأب والأم متوفيين مين بصير رب الأسرة بالدفتر؟"},
            {"message_id": "ammiya_08_03", "question": "لو كان الأخ الكبير متزوج ومستقل، مين بياخد مكانه؟"},
            {"message_id": "ammiya_08_04", "question": "كم بدفعوا رسوم بهالحالة للدفتر؟"}
        ]
    })

    # Chat 9: شروط وأسئلة مفخخة بالعامية
    chats.append({
        "chat_id": "ammiya_chat_09",
        "messages": [
            {"message_id": "ammiya_09_01", "question": "لازم جوزي ييجي معي ويوقع موافقة عشان أطلع جواز سفري؟"},
            {"message_id": "ammiya_09_02", "question": "بقدر أجدد جوازي وعمره باقي فيه سنتين بدون ما يكون عندي فيزا أو سبب؟"},
            {"message_id": "ammiya_09_03", "question": "بدهم عدم محكومية عشان أعمل هوية ذكية؟"},
            {"message_id": "ammiya_09_04", "question": "إذا جبت ورقة بلاغ من المركز الأمني بيعفوني من رسوم بدل فاقد الهوية؟"}
        ]
    })

    # Chat 10: الصور الشخصية بالعامية
    chats.append({
        "chat_id": "ammiya_chat_10",
        "messages": [
            {"message_id": "ammiya_10_01", "question": "كم صورة شخصية بدهم لجواز السفر أول مرة؟"},
            {"message_id": "ammiya_10_02", "question": "ولتجديد الجواز كم صورة بدي؟"},
            {"message_id": "ammiya_10_03", "question": "وللبطاقة الذكية لأول مرة كم صورة بياخدوا؟"},
            {"message_id": "ammiya_10_04", "question": "ودفتر العيلة بده صور شخصية شي؟"}
        ]
    })

    # Chat 11: أسئلة خارج النطاق بالعامية
    chats.append({
        "chat_id": "ammiya_chat_11",
        "messages": [
            {"message_id": "ammiya_11_01", "question": "بدي أجدد رخصة السواقة الخصوصي شو الإجراءات بالمرو؟"},
            {"message_id": "ammiya_11_02", "question": "علي مخالفات سير كيف بعترض عليها بالأمانة؟"},
            {"message_id": "ammiya_11_03", "question": "بدي أصدق شهادة التوجيهي من التربية والتعليم وين أروح؟"},
            {"message_id": "ammiya_11_04", "question": "شو أحسن مطعم منسف بإربد وكم سعر السدر؟"}
        ]
    })

    # Chat 12: أسئلة غامضة بالعامية
    chats.append({
        "chat_id": "ammiya_chat_12",
        "messages": [
            {"message_id": "ammiya_12_01", "question": "بدي أجدد شو الأوراق المطلوبة؟"},
            {"message_id": "ammiya_12_02", "question": "ضاع مني شو أسوي وكيف أتصرف؟"},
            {"message_id": "ammiya_12_03", "question": "كم بكلفني الإصدار أول مرة؟"},
            {"message_id": "ammiya_12_04", "question": "قديش بتقعد المعاملة لتخلص؟"}
        ]
    })

    # Chat 13: السفر والمدة المتبقية
    chats.append({
        "chat_id": "ammiya_chat_13",
        "messages": [
            {"message_id": "ammiya_03_01", "question": "جوازي باقي عليه 4 شهور بقدر أجدده ولا لأ؟"},
            {"message_id": "ammiya_03_02", "question": "كم بدفع رسوم عليه بما إنه أقل من 180 يوم؟"},
            {"message_id": "ammiya_03_03", "question": "وجواز الصغار كم سنة بكون صالح؟"},
            {"message_id": "ammiya_03_04", "question": "وجواز الكبار اللي عمرهم فوق 16 كم سنة بصمد؟"}
        ]
    })

    # Chat 14: فصل دفتر العيلة للمطلقة
    chats.append({
        "chat_id": "ammiya_chat_14",
        "messages": [
            {"message_id": "ammiya_14_01", "question": "أنا مطلقة وبدي أفصل دفتر عيلة لحالي، شو الشروط؟"},
            {"message_id": "ammiya_14_02", "question": "شو الأوراق اللي لازم أقدمها؟"},
            {"message_id": "ammiya_14_03", "question": "والأرملة كمان بتقدر تطلع دفتر مستقل؟"},
            {"message_id": "ammiya_14_04", "question": "كم بدفع رسوم على فصل دفتر العائلة؟"}
        ]
    })

    # Chat 15: السفارات والأردنيين بالخارج
    chats.append({
        "chat_id": "ammiya_chat_15",
        "messages": [
            {"message_id": "ammiya_15_01", "question": "أنا مغترب بقطر وبدي أجدد جوازي، بقدر أعمله من السفارة بالدوحة؟"},
            {"message_id": "ammiya_15_02", "question": "ولو باسبوري ضاع بالخارج السفارة بتطلعلي بدل فاقد؟"},
            {"message_id": "ammiya_15_03", "question": "وبقدر أطلع الهوية الذكية من السفارة برا البلد؟"},
            {"message_id": "ammiya_15_04", "question": "وين لازم أروح عشان الهوية الذكية حصراً؟"}
        ]
    })

    # Chat 16: زمرة الدم وتطبيق سند
    chats.append({
        "chat_id": "ammiya_chat_16",
        "messages": [
            {"message_id": "ammiya_16_01", "question": "لازم فحص دم عشان يعرفوا زمرة دمي بالهوية الذكية؟"},
            {"message_id": "ammiya_16_02", "question": "إذا معي رخصة قديمة مكتوب عليها زمرة الدم بمشوا فيها؟"},
            {"message_id": "ammiya_16_03", "question": "الهوية الذكية بتفعل تطبيق سند والرقم السري؟"},
            {"message_id": "ammiya_16_04", "question": "في رسوم زيادة على تفعيل سند والشريحة؟"}
        ]
    })

    # Chat 17: خدمة العلم وموافقة الجيش
    chats.append({
        "chat_id": "ammiya_chat_17",
        "messages": [
            {"message_id": "ammiya_17_01", "question": "الشباب اللي بعمر خدمة العلم شو بدهم موافقة للجواز أول مرة؟"},
            {"message_id": "ammiya_17_02", "question": "دفتر خدمة العلم لازم يكون مؤجل ومختوم؟"},
            {"message_id": "ammiya_17_03", "question": "وبدل فاقد الجواز بده موافقة أمنية؟"},
            {"message_id": "ammiya_17_04", "question": "كم يوم بتقعد الموافقة الأمنية لتطلع؟"}
        ]
    })

    # Chat 18: استلام المعاملة والدور
    chats.append({
        "chat_id": "ammiya_chat_18",
        "messages": [
            {"message_id": "ammiya_18_01", "question": "أول ما أفوت مكتب الأحوال عشان أعمل هوية ذكية شو بعمل أول خطوة؟"},
            {"message_id": "ammiya_18_02", "question": "وين بنتصور وبناخد البصمات؟"},
            {"message_id": "ammiya_18_03", "question": "وين بدفع الرسوم عند أي شباك؟"},
            {"message_id": "ammiya_18_04", "question": "بقدر أبعث صاحبي يستلم هويتي بدالي؟"}
        ]
    })

    # Chat 19: تأخير زواج وغرامات
    chats.append({
        "chat_id": "ammiya_chat_19",
        "messages": [
            {"message_id": "ammiya_19_01", "question": "قديش معنا مهلة نسجل الزواج بدون غرامة؟"},
            {"message_id": "ammiya_19_02", "question": "إذا صرلي 110 أيام متزوج كم بنزل علي غرامة؟"},
            {"message_id": "ammiya_19_03", "question": "كم بصير كل المبلغ اللي بدفعه لدفتر العيلة؟"},
            {"message_id": "ammiya_19_04", "question": "وإذا سجلت باليوم السبعين بنزل علي غرامة شي؟"}
        ]
    })

    # Chat 20: الجواز التالف
    chats.append({
        "chat_id": "ammiya_chat_20",
        "messages": [
            {"message_id": "ammiya_20_01", "question": "جوازي انكب عليه شاي وانبل، بعتبروه تالف؟"},
            {"message_id": "ammiya_20_02", "question": "لازم أجيب الجواز المبلول معي وأسلمه؟"},
            {"message_id": "ammiya_20_03", "question": "كم بدفع رسوم على الجواز التالف؟"},
            {"message_id": "ammiya_20_04", "question": "وقديش بقعد بالمكتب لتطلع النسخة الجديدة؟"}
        ]
    })

    # Chat 21: الهوية الضايعة
    chats.append({
        "chat_id": "ammiya_chat_21",
        "messages": [
            {"message_id": "ammiya_21_01", "question": "ضاعت هويتي وأنا بالسوق، شو أول شي أعمله؟"},
            {"message_id": "ammiya_21_02", "question": "لازم أروح على المخفر أعمل بلاغ؟"},
            {"message_id": "ammiya_21_03", "question": "كم بكلفني بدل الفاقد؟"},
            {"message_id": "ammiya_21_04", "question": "متى بستلم الهوية الجديدة؟"}
        ]
    })

    # Chat 22: إضافة ولد جديد لدفتر العيلة
    chats.append({
        "chat_id": "ammiya_chat_22",
        "messages": [
            {"message_id": "ammiya_22_01", "question": "إجاني مولود جديد الحمد لله، شو بدي أوراق لأضيفه على دفتر العيلة؟"},
            {"message_id": "ammiya_22_02", "question": "كم بدفع رسوم على إضافة المولود؟"},
            {"message_id": "ammiya_22_03", "question": "وإذا الدفتر كان مليان صفحات وبدهم يبدلوه كم بياخدوا؟"},
            {"message_id": "ammiya_22_04", "question": "رسم تجديد دفتر العيلة المليان كم هو؟"}
        ]
    })

    # Chat 23: مقارنات ورسوم مختلفة
    chats.append({
        "chat_id": "ammiya_chat_23",
        "messages": [
            {"message_id": "ammiya_23_01", "question": "بقدر أعمل تجديد للجواز وأطلع هوية ذكية بنفس اليوم والمكتب؟"},
            {"message_id": "ammiya_23_02", "question": "كم التكلفة كاملة للخدمتين مع بعض؟"},
            {"message_id": "ammiya_23_03", "question": "كم صورة أجهز معي بالزبط؟"},
            {"message_id": "ammiya_23_04", "question": "كم بياخدوا وقت الاتنين مع بعض؟"}
        ]
    })

    # Chat 24: الأماكن والمكاتب المعتمدة
    chats.append({
        "chat_id": "ammiya_chat_24",
        "messages": [
            {"message_id": "ammiya_24_01", "question": "وين مكاتب الأحوال المدنية بإربد وعمان؟"},
            {"message_id": "ammiya_24_02", "question": "المواطن العازب لحاله بطلعله دفتر عيلة؟"},
            {"message_id": "ammiya_24_03", "question": "مين هم الفئات المستفيدة من دفتر العيلة؟"},
            {"message_id": "ammiya_24_04", "question": "بقدر أقدم طلب دفتر عيلة من السفارة وأنا مسافر؟"}
        ]
    })

    # Chat 25: تأكيد الأرقام النهائية بالعامية
    chats.append({
        "chat_id": "ammiya_chat_25",
        "messages": [
            {"message_id": "ammiya_25_01", "question": "واحد عمره 20 سنة كم بدفع على أول جواز سفر؟"},
            {"message_id": "ammiya_25_02", "question": "الهوية الذكية بدل فاقد أول مرة كم بتكلف؟"},
            {"message_id": "ammiya_25_03", "question": "غرامة تأخير دفتر العيلة بعد 3 شهور كم دينار؟"},
            {"message_id": "ammiya_25_04", "question": "ورسم دفتر العائلة الأساسي أول مرة كم هو؟"}
        ]
    })

    return {"chats": chats}


def create_english_chats():
    chats = []
    # 25 chats, 4 msgs each = 100 questions in English
    
    # Chat 1: First Issue Passport
    chats.append({
        "chat_id": "en_chat_01",
        "messages": [
            {"message_id": "en_01_01", "question": "What are the required documents to issue a Jordanian passport for the first time for someone aged 16 or older?"},
            {"message_id": "en_01_02", "question": "How much is the official fee for this age group?"},
            {"message_id": "en_01_03", "question": "What is the fee if the applicant is under 16 years old?"},
            {"message_id": "en_01_04", "question": "Is written guardian consent mandatory for minors under 18?"}
        ]
    })

    # Chat 2: Passport Renewal & Locations
    chats.append({
        "chat_id": "en_chat_02",
        "messages": [
            {"message_id": "en_02_01", "question": "How much is the renewal fee for an expired regular passport inside Jordan?"},
            {"message_id": "en_02_02", "question": "If the passport has full pages before its expiration, what is the fee?"},
            {"message_id": "en_02_03", "question": "Where can a Jordanian citizen living abroad submit the renewal application?"},
            {"message_id": "en_02_04", "question": "How long does it take to process passport renewal at department offices?"}
        ]
    })

    # Chat 3: Lost & Damaged Passport Comparison
    chats.append({
        "chat_id": "en_chat_03",
        "messages": [
            {"message_id": "en_03_01", "question": "What is the fee for issuing a replacement for a lost passport for the first time?"},
            {"message_id": "en_03_02", "question": "What is the fee if the passport is lost for the second time or more?"},
            {"message_id": "en_03_03", "question": "How much is the fee for issuing a replacement for a damaged passport?"},
            {"message_id": "en_03_04", "question": "Which service has higher fees: replacement for damaged passport or replacement for lost passport for the first time?"}
        ]
    })

    # Chat 4: Smart ID Card First Issue
    chats.append({
        "chat_id": "en_chat_04",
        "messages": [
            {"message_id": "en_04_01", "question": "What are the conditions and documents required to issue a smart ID card for the first time at age 16?"},
            {"message_id": "en_04_02", "question": "What documents must be submitted for the first smart ID card?"},
            {"message_id": "en_04_03", "question": "What is the official fee for issuing the smart ID card for the first time?"},
            {"message_id": "en_04_04", "question": "How long does it take to issue and receive the smart ID card?"}
        ]
    })

    # Chat 5: Smart ID Card Renewal & Replacements
    chats.append({
        "chat_id": "en_chat_05",
        "messages": [
            {"message_id": "en_05_01", "question": "How much does it cost to renew an expired smart ID card?"},
            {"message_id": "en_05_02", "question": "What is the fee for a replacement damaged smart ID card if broken?"},
            {"message_id": "en_05_03", "question": "How much is the fee for issuing a replacement for a lost smart ID card?"},
            {"message_id": "en_05_04", "question": "What documents are required to apply for a lost smart ID card replacement?"}
        ]
    })

    # Chat 6: Family Book First Issue & Marriage Delay
    chats.append({
        "chat_id": "en_chat_06",
        "messages": [
            {"message_id": "en_06_01", "question": "What documents are needed to issue a family book for the first time after marriage?"},
            {"message_id": "en_06_02", "question": "How much is the fee to issue a family book for the first time within the legal deadline?"},
            {"message_id": "en_06_03", "question": "If I apply 4 months after getting married, what is the total cost including the late penalty fee?"},
            {"message_id": "en_06_04", "question": "What is the legal grace period allowed before a late fee is applied?"}
        ]
    })

    # Chat 7: Family Book Renewal, Lost, & Damaged
    chats.append({
        "chat_id": "en_chat_07",
        "messages": [
            {"message_id": "en_07_01", "question": "How much does it cost to renew a family book when it is completely full of children names?"},
            {"message_id": "en_07_02", "question": "What is the fee for issuing a replacement for a lost family book?"},
            {"message_id": "en_07_03", "question": "How much is the fee for a replacement for a damaged family book?"},
            {"message_id": "en_07_04", "question": "Which is more expensive: a replacement for a lost family book or a damaged family book?"}
        ]
    })

    # Chat 8: Deceased Parents & Head of Family
    chats.append({
        "chat_id": "en_chat_08",
        "messages": [
            {"message_id": "en_08_01", "question": "In the event of the father death, is the widow entitled to a family book in her name?"},
            {"message_id": "en_08_02", "question": "If both the father and mother have passed away, who becomes the head of the family in the family book?"},
            {"message_id": "en_08_03", "question": "What are the rules if the eldest child is married?"},
            {"message_id": "en_08_04", "question": "What is the fee for issuing a family book in this case?"}
        ]
    })

    # Chat 9: False Assumptions Correction (English)
    chats.append({
        "chat_id": "en_chat_09",
        "messages": [
            {"message_id": "en_09_01", "question": "Is husband written consent required for a Jordanian wife to obtain a passport?"},
            {"message_id": "en_09_02", "question": "Can a citizen renew their passport if there are two years of validity remaining without any travel reason?"},
            {"message_id": "en_09_03", "question": "Do I need a criminal record clearance certificate to issue a smart ID card for the first time?"},
            {"message_id": "en_09_04", "question": "Is a citizen exempt from lost ID card fees if they bring a police report?"}
        ]
    })

    # Chat 10: Photo Requirements (English)
    chats.append({
        "chat_id": "en_chat_10",
        "messages": [
            {"message_id": "en_10_01", "question": "How many personal photos are required to issue a passport for the first time?"},
            {"message_id": "en_10_02", "question": "How many personal photos are needed for passport renewal?"},
            {"message_id": "en_10_03", "question": "How many photos are required to issue a smart ID card for minors under 18?"},
            {"message_id": "en_10_04", "question": "Are personal photos required when issuing a family book?"}
        ]
    })

    # Chat 11: Out of Scope Inquiries (English)
    chats.append({
        "chat_id": "en_chat_11",
        "messages": [
            {"message_id": "en_11_01", "question": "How can I attest my university degree from the Ministry of Higher Education?"},
            {"message_id": "en_11_02", "question": "What are the fees for renewing a driver license at the traffic department?"},
            {"message_id": "en_11_03", "question": "How much is the municipal property tax for residential buildings in Amman?"},
            {"message_id": "en_11_04", "question": "What are the best flight booking options to Dubai via Royal Jordanian?"}
        ]
    })

    # Chat 12: Ambiguous Inquiries (English)
    chats.append({
        "chat_id": "en_chat_12",
        "messages": [
            {"message_id": "en_12_01", "question": "I want to renew my official document, what are the requirements and fees?"},
            {"message_id": "en_12_02", "question": "I lost my document, what legal procedure should I follow?"},
            {"message_id": "en_12_03", "question": "How long does the service take at government offices?"},
            {"message_id": "en_12_04", "question": "What is the total fee required for issuing for the first time?"}
        ]
    })

    # Chat 13: Passport Validity & Early Renewal
    chats.append({
        "chat_id": "en_chat_13",
        "messages": [
            {"message_id": "en_13_01", "question": "Do passport renewal fees differ if the passport is valid for more than 180 days?"},
            {"message_id": "en_13_02", "question": "How much is the renewal fee if the remaining validity is more than 180 days?"},
            {"message_id": "en_13_03", "question": "What is the validity period of a passport granted to persons under 16 years old?"},
            {"message_id": "en_13_04", "question": "What is the passport validity period for someone aged 16 or older?"}
        ]
    })

    # Chat 14: Family Book Separation (Divorce & Widowhood)
    chats.append({
        "chat_id": "en_chat_14",
        "messages": [
            {"message_id": "en_14_01", "question": "What are the conditions and procedures for a divorced woman to obtain an independent family book?"},
            {"message_id": "en_14_02", "question": "What documents are required for family book separation for a divorced woman?"},
            {"message_id": "en_14_03", "question": "Can a widowed woman obtain an independent family book?"},
            {"message_id": "en_14_04", "question": "What is the fee for separating or issuing a family book in this situation?"}
        ]
    })

    # Chat 15: Partner Institutions & Military Approvals
    chats.append({
        "chat_id": "en_chat_15",
        "messages": [
            {"message_id": "en_15_01", "question": "Who are the partner entities involved in issuing a passport for the first time?"},
            {"message_id": "en_15_02", "question": "What is the role of the Jordan Armed Forces or Military Service Office in passport transactions?"},
            {"message_id": "en_15_03", "question": "Does a replacement for a lost passport require security clearance from the Public Security Directorate?"},
            {"message_id": "en_15_04", "question": "Which security partner is involved in issuing a replacement for a lost smart ID card?"}
        ]
    })

    # Chat 16: Blood Type & Sanad Digital Identity
    chats.append({
        "chat_id": "en_chat_16",
        "messages": [
            {"message_id": "en_16_01", "question": "Is a blood type medical test required when issuing a smart ID card for the first time?"},
            {"message_id": "en_16_02", "question": "Can blood type be verified based on an old driver license?"},
            {"message_id": "en_16_03", "question": "Does the smart ID card include an electronic chip to activate digital identity via Sanad app?"},
            {"message_id": "en_16_04", "question": "Are there extra fees to activate the PIN code or digital chip of the card?"}
        ]
    })

    # Chat 17: Consular & Embassy Services
    chats.append({
        "chat_id": "en_chat_17",
        "messages": [
            {"message_id": "en_17_01", "question": "Can a Jordanian citizen living in the United Kingdom renew their passport at the Jordanian Embassy in London?"},
            {"message_id": "en_17_02", "question": "Can they also issue a replacement for a lost passport at the embassy?"},
            {"message_id": "en_17_03", "question": "Can smart ID cards be issued or renewed at embassies and consulates outside Jordan?"},
            {"message_id": "en_17_04", "question": "Where must a citizen apply for a smart ID card exclusively?"}
        ]
    })

    # Chat 18: Step-by-Step Office Procedures
    chats.append({
        "chat_id": "en_chat_18",
        "messages": [
            {"message_id": "en_18_01", "question": "What is the first step upon arriving at the Civil Status office to issue a smart ID card?"},
            {"message_id": "en_18_02", "question": "What are the procedures for capturing personal photos and ten fingerprints?"},
            {"message_id": "en_18_03", "question": "Where are the official fees paid for the smart ID card?"},
            {"message_id": "en_18_04", "question": "Who is legally authorized to receive the printed smart ID card?"}
        ]
    })

    # Chat 19: Marriage Registration Deadlines & Arithmetic
    chats.append({
        "chat_id": "en_chat_19",
        "messages": [
            {"message_id": "en_19_01", "question": "What is the legal deadline for registering a marriage without incurring a financial penalty?"},
            {"message_id": "en_19_02", "question": "If 100 days have passed since the marriage contract, how much is the legal late penalty fee?"},
            {"message_id": "en_19_03", "question": "What becomes the total amount due for the family book including fee and penalty?"},
            {"message_id": "en_19_04", "question": "If the family book is issued on the 80th day after marriage, is there any penalty fee?"}
        ]
    })

    # Chat 20: Damaged Document Definition
    chats.append({
        "chat_id": "en_chat_20",
        "messages": [
            {"message_id": "en_20_01", "question": "When is a passport legally considered damaged?"},
            {"message_id": "en_20_02", "question": "Does tearing of the passport cover or water damage require issuing a replacement for a damaged passport?"},
            {"message_id": "en_20_03", "question": "Must the old damaged passport be surrendered to the Civil Status Department upon application?"},
            {"message_id": "en_20_04", "question": "What is the fee for issuing a replacement for a damaged passport?"}
        ]
    })

    # Chat 21: Lost ID Card Procedures
    chats.append({
        "chat_id": "en_chat_21",
        "messages": [
            {"message_id": "en_21_01", "question": "What steps should be taken immediately upon losing a smart ID card?"},
            {"message_id": "en_21_02", "question": "Is a formal police report required when losing a smart ID card?"},
            {"message_id": "en_21_03", "question": "How much does a replacement for a lost smart ID card cost?"},
            {"message_id": "en_21_04", "question": "What is the expected turnaround time to receive the replacement card?"}
        ]
    })

    # Chat 22: Adding Newborns to Family Book (English)
    chats.append({
        "chat_id": "en_chat_22",
        "messages": [
            {"message_id": "en_22_01", "question": "What documents are required to register a newborn in the family book?"},
            {"message_id": "en_22_02", "question": "How much is the fee to add a newborn child to the family book?"},
            {"message_id": "en_22_03", "question": "If the family book has no empty pages left, does it need to be renewed?"},
            {"message_id": "en_22_04", "question": "How much is the renewal fee for a completely full family book?"}
        ]
    })

    # Chat 23: Simultaneous Multiple Services
    chats.append({
        "chat_id": "en_chat_23",
        "messages": [
            {"message_id": "en_23_01", "question": "Can a citizen apply for passport renewal and first-time smart ID card in the same visit?"},
            {"message_id": "en_23_02", "question": "What is the combined total fee for renewing an expired passport and issuing a first-time smart ID card?"},
            {"message_id": "en_23_03", "question": "How many total personal photos should be prepared to cover both services?"},
            {"message_id": "en_23_04", "question": "What is the processing time for each service at the department?"}
        ]
    })

    # Chat 24: Single Citizens & Eligibility
    chats.append({
        "chat_id": "en_chat_24",
        "messages": [
            {"message_id": "en_24_01", "question": "Is an independent family book issued to an unmarried single Jordanian citizen?"},
            {"message_id": "en_24_02", "question": "Who are the eligible beneficiary categories for the family book service?"},
            {"message_id": "en_24_03", "question": "Where are the official headquarters and service locations of the Civil Status Department located?"},
            {"message_id": "en_24_04", "question": "Can a Jordanian citizen abroad request a family book through embassies?"}
        ]
    })

    # Chat 25: Official Numbers Verification
    chats.append({
        "chat_id": "en_chat_25",
        "messages": [
            {"message_id": "en_25_01", "question": "What is the fee to issue a passport for the first time for a citizen aged 20 years?"},
            {"message_id": "en_25_02", "question": "What is the fee for a replacement lost smart ID card for the first time?"},
            {"message_id": "en_25_03", "question": "What is the late penalty fee for issuing a family book after 90 days from marriage?"},
            {"message_id": "en_25_04", "question": "What is the basic issuance fee for a family book for the first time?"}
        ]
    })

    return {"chats": chats}


def main():
    fusha_data = create_fusha_chats()
    ammiya_data = create_ammiya_chats()
    en_data = create_english_chats()

    with open("test_100_fusha.json", "w", encoding="utf-8") as f:
        json.dump(fusha_data, f, ensure_ascii=False, indent=2)

    with open("test_100_ammiya.json", "w", encoding="utf-8") as f:
        json.dump(ammiya_data, f, ensure_ascii=False, indent=2)

    with open("test_100_english.json", "w", encoding="utf-8") as f:
        json.dump(en_data, f, ensure_ascii=False, indent=2)

    # Master combined test suite with 300 questions (75 chats)
    master_chats = fusha_data["chats"] + ammiya_data["chats"] + en_data["chats"]
    with open("test_300_master.json", "w", encoding="utf-8") as f:
        json.dump({"chats": master_chats}, f, ensure_ascii=False, indent=2)

    print(f"Generated test_100_fusha.json: {len(fusha_data['chats'])} chats ({len(fusha_data['chats'])*4} questions)")
    print(f"Generated test_100_ammiya.json: {len(ammiya_data['chats'])} chats ({len(ammiya_data['chats'])*4} questions)")
    print(f"Generated test_100_english.json: {len(en_data['chats'])} chats ({len(en_data['chats'])*4} questions)")
    print(f"Generated test_300_master.json: {len(master_chats)} chats ({len(master_chats)*4} questions)")

if __name__ == "__main__":
    main()
