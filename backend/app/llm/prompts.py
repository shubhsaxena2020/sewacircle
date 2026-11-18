"""Prompts for role extraction and evidence drafting. Few-shot examples are invented and are NOT taken from the eval set."""
from __future__ import annotations

from ..taxonomy import SKILLS

# Hindi aliases help the model map dialect/Hindi phrasing to taxonomy ids (R2/R4 recommendation).
_HINDI_ALIASES = {
    "first_aid": "प्राथमिक उपचार, फर्स्ट एड", "health_education": "स्वास्थ्य शिक्षा, स्वास्थ्य जानकारी",
    "hygiene_promotion": "स्वच्छता, हाथ धोना, सफाई जागरूकता", "logistics_supplies": "सामान, व्यवस्था, सप्लाई",
    "driving_transport": "गाड़ी, ड्राइवर, वाहन", "dialect_awadhi": "अवधी, स्थानीय बोली (अवध क्षेत्र)",
    "dialect_bhojpuri": "भोजपुरी, स्थानीय बोली (पूर्वांचल)", "community_mobilisation": "लोगों को जुटाना, घर-घर संपर्क",
    "team_leadership": "टीम का नेतृत्व, अगुवाई", "event_coordination": "कार्यक्रम संचालन, समन्वय",
    "documentation_reporting": "रिपोर्ट, रजिस्टर, उपस्थिति, लिखा-पढ़ी", "photography_video": "फोटो, वीडियो",
    "graphic_design": "पोस्टर, डिज़ाइन", "teaching_literacy": "पढ़ाना, साक्षरता", "counselling_support": "परामर्श, काउंसलिंग",
    "sports_coaching": "खेल प्रशिक्षण, कोच", "tech_digital_support": "मोबाइल, कंप्यूटर, डिजिटल मदद, UPI",
    "food_distribution": "भोजन, राशन वितरण", "tree_plantation": "पौधारोपण, पेड़ लगाना",
    "disaster_response": "बाढ़, आपदा राहत, बचाव", "fundraising_outreach": "चंदा, दान, साझेदार",
}

TAXONOMY_TEXT = "\n".join(f"- {k}: {v}" + (f" ({_HINDI_ALIASES[k]})" if k in _HINDI_ALIASES else "") for k, v in SKILLS.items())

EXTRACT_SYSTEM = f"""You turn a volunteer organiser's task description (Hindi, English, Hinglish or Awadhi/Bhojpuri-flavoured Hindi)
into the ROLES the task needs. Output ONLY one minified JSON object, no prose, no code fences:
{{"roles":[{{"role":"short English role name","count":int,"required_skills":["taxonomy_id",...],"evidence_span":"exact words copied from the text that justify this role","confidence":"high|medium|low","reason":"one short English sentence"}}],"needs_decision":["question for the organiser"],"language_detected":"hi|en|hinglish"}}

Rules:
1. required_skills MUST be ids from this list only (any one of them qualifies a person). Use [] when anyone can do the role.
{TAXONOMY_TEXT}
2. evidence_span must be copied verbatim from the input (keep the original script). Never invent a span.
3. count: use a number stated in the text (Devanagari digits allowed, e.g. २ = 2). If the text gives none, use 1 and set confidence to medium.
   Never multiply by the crowd size: 120 attendees does not mean 120 volunteers.
4. Only include roles the text asks for or clearly implies. Do not add roles the text does not support.
5. If something important is unclear (exact count, which dialect, permissions, safety), add a short question to needs_decision instead of guessing.
6. Negation matters: "no driver needed" means no driver role.
7. The text may contain placeholders like [PHONE] or [AADHAAR] where personal data was removed; ignore them.
"""

EXTRACT_FEWSHOT = [
    ("रविवार को पार्क की सफाई है। 3 लोग झाड़ू लगाने के लिए और एक व्यक्ति जो टीम संभाल सके। फोटो की ज़रूरत नहीं है।",
     '{"roles":[{"role":"Cleaning volunteer","count":3,"required_skills":[],"evidence_span":"3 लोग झाड़ू लगाने के लिए","confidence":"high","reason":"Three people are asked for cleaning."},'
     '{"role":"Team lead","count":1,"required_skills":["team_leadership","event_coordination"],"evidence_span":"एक व्यक्ति जो टीम संभाल सके","confidence":"high","reason":"One person should manage the team."}],'
     '"needs_decision":[],"language_detected":"hi"}'),
    ("Need volunteers for a vaccination awareness walk on Saturday. Someone who speaks Bhojpuri, two people for posters, and a first aider just in case.",
     '{"roles":[{"role":"Local-language liaison (Bhojpuri)","count":1,"required_skills":["dialect_bhojpuri"],"evidence_span":"Someone who speaks Bhojpuri","confidence":"high","reason":"Explicitly asked for a Bhojpuri speaker."},'
     '{"role":"Poster team","count":2,"required_skills":["graphic_design"],"evidence_span":"two people for posters","confidence":"high","reason":"Two poster makers requested."},'
     '{"role":"First-aid support","count":1,"required_skills":["first_aid"],"evidence_span":"a first aider just in case","confidence":"high","reason":"A first aider is requested."}],'
     '"needs_decision":["Is a health educator needed for the vaccination messages?"],"language_detected":"en"}'),
    ("Kal library mein bachchon ko padhana hai, kuch teachers chahiye aur ek banda attendance register sambhale.",
     '{"roles":[{"role":"Teacher","count":1,"required_skills":["teaching_literacy"],"evidence_span":"kuch teachers chahiye","confidence":"medium","reason":"Teachers requested but the number is not given."},'
     '{"role":"Attendance keeper","count":1,"required_skills":["documentation_reporting"],"evidence_span":"ek banda attendance register sambhale","confidence":"high","reason":"One person for the attendance register."}],'
     '"needs_decision":["How many teachers are needed (text says kuch)?"],"language_detected":"hinglish"}'),
]

DRAFT_SYSTEM = """You draft volunteer CONTRIBUTION CARDS from a host's short notes after a community event. You are a drafting aid:
a human host will confirm, correct or reject every card. Output ONLY one minified JSON object, no prose, no code fences:
{"cards":[{"volunteer_id":"id from the roster list","role":"role name","claimed_hours":number,"summary":"one factual English sentence of what the notes say this person did","evidence":"exact words copied from the notes"}]}

Rules:
1. One card per volunteer mentioned in the notes or listed on the roster. Use ONLY volunteer ids from the roster list given.
2. claimed_hours = the hours the NOTES attribute to that person. If the notes give no hours for them, use 0 and say so in the summary.
3. Never invent work the notes do not mention. Never call anything verified or confirmed.
4. evidence must be copied verbatim from the notes ("" if the person is not mentioned).
"""
