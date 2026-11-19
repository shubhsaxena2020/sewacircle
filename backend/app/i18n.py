"""Localized display text for the organiser screen: English (canonical) and Hindi.

Scope, stated honestly
----------------------
This module localizes the *fixed* text the server itself writes: task titles, role
names, skill labels, slot names, the READY/NOT READY verdict and the recruit-request
and reason templates produced by ``solver/ready.py`` and ``solver/cp_sat.py``. It
does NOT translate anything a language model wrote (contribution-card summaries and
evidence text stay in whatever language the host wrote them in) and it does not
transliterate proper nouns: district and block names are place names and are left
exactly as they are.

Why the Hindi is built from structured facts, not translated from the English string
-----------------------------------------------------------------------------------
The English reasons are assembled from solver facts (role, needed count, skills,
slot, area, travel limit). Translating the finished sentence would let the two
languages drift, so the Hindi rendering is built from the SAME fields. That is what
makes the contract test possible: ids, counts and decisions are identical in both
languages because they come from one object, and only the words change.

Per-pick reasons go one step further: ``solver/cp_sat.py`` writes
``Assignment.reason_codes`` (code + params) and the English sentences are rendered from
them with :func:`reason_text`; the Hindi sentences are the same function with ``"hi"``.
So the skill level, the distance in whole km, the "not picked in N days" window, the
newcomer count and the mentor's name are the same facts in both languages, not a
summary of a sentence.

Fallback rule
-------------
A role name or title this module does not know (for example a role the organiser
typed, or one the AI extracted from the brief) is returned UNCHANGED in both
languages. We do not machine-translate and we do not invent a translation; an
untranslated but correct label beats a confident wrong one.
"""
from __future__ import annotations

from typing import Literal

from .schemas import (AssignmentDisplay, PickReason, RecruitDisplay, RoleDisplay, RosterDisplay, RoleSpec, RosterResult,
                      SkillLabel, TaskDisplay, TaskSpec)
from .taxonomy import SKILLS

Lang = Literal["en", "hi"]

#: Hand-written Hindi labels for the 24 taxonomy skills (same ids, same meaning).
SKILL_LABELS_HI: dict[str, str] = {
    "first_aid": "प्राथमिक उपचार",
    "health_education": "स्वास्थ्य शिक्षा और जागरूकता",
    "hygiene_promotion": "स्वच्छता और साफ़-सफ़ाई का प्रचार",
    "logistics_supplies": "सामान, व्यवस्था और साइट सेटअप",
    "driving_transport": "गाड़ी चलाना / परिवहन",
    "dialect_awadhi": "अवधी बोलने वाला (स्थानीय भाषा में संपर्क)",
    "dialect_bhojpuri": "भोजपुरी बोलने वाला (स्थानीय भाषा में संपर्क)",
    "hindi_fluent": "धाराप्रवाह हिंदी",
    "english_fluent": "धाराप्रवाह अंग्रेज़ी",
    "urdu_fluent": "धाराप्रवाह उर्दू",
    "community_mobilisation": "समुदाय जुटाना / घर-घर संपर्क",
    "team_leadership": "टीम का नेतृत्व",
    "event_coordination": "कार्यक्रम का समन्वय",
    "documentation_reporting": "दस्तावेज़, उपस्थिति और रिपोर्टिंग",
    "photography_video": "फ़ोटोग्राफ़ी / वीडियो",
    "graphic_design": "पोस्टर और ग्राफ़िक डिज़ाइन",
    "teaching_literacy": "पढ़ाना / साक्षरता सहायता",
    "counselling_support": "परामर्श और मनोसामाजिक सहायता",
    "sports_coaching": "खेल प्रशिक्षण",
    "tech_digital_support": "डिजिटल और तकनीकी सहायता",
    "food_distribution": "खाना बनाना और भोजन वितरण",
    "tree_plantation": "पौधारोपण / कृषि",
    "disaster_response": "आपदा प्रतिक्रिया और बचाव की बुनियादी जानकारी",
    "fundraising_outreach": "धन जुटाना और साझेदार संपर्क",
}

#: Hindi titles for the synthetic drives this prototype ships with.
TITLE_LABELS_HI: dict[str, str] = {
    "Water and hygiene camp": "पेयजल और स्वच्छता शिविर",
    "Blood donation camp": "रक्तदान शिविर",
    "Tree plantation drive": "पौधारोपण अभियान",
    "Evening literacy class": "शाम की साक्षरता कक्षा",
    "Flood relief distribution": "बाढ़ राहत वितरण",
    "Block sports day": "ब्लॉक खेल दिवस",
    "Health awareness camp": "स्वास्थ्य जागरूकता शिविर",
    "Cleanliness drive": "सफ़ाई अभियान",
    "Digital literacy for elders": "बुज़ुर्गों के लिए डिजिटल साक्षरता",
    "Elderly care visits": "बुज़ुर्गों की देखभाल के दौरे",
}

#: Hindi role names for the roles in the synthetic drives (and common brief roles).
ROLE_LABELS_HI: dict[str, str] = {
    "Team lead": "टीम लीड",
    "Local-language liaison": "स्थानीय भाषा संपर्क",
    "First-aid support": "प्राथमिक उपचार सहायता",
    "Logistics and supplies": "सामान और व्यवस्था",
    "Hygiene educator": "स्वच्छता शिक्षक",
    "Documentation": "दस्तावेज़ीकरण",
    "Donor registration": "रक्तदाता पंजीकरण",
    "Community mobiliser": "समुदाय संपर्ककर्ता",
    "Supplies": "सामान",
    "Planting team": "पौधारोपण टीम",
    "Sapling logistics": "पौधों की व्यवस्था",
    "Photos and report": "फ़ोटो और रिपोर्ट",
    "Teacher": "शिक्षक",
    "Parent liaison (Bhojpuri)": "अभिभावक संपर्क (भोजपुरी)",
    "Attendance and records": "उपस्थिति और अभिलेख",
    "Relief lead": "राहत प्रमुख",
    "Driver and supplies": "चालक और सामान",
    "Food distribution": "भोजन वितरण",
    "Local liaison (Bhojpuri)": "स्थानीय संपर्क (भोजपुरी)",
    "Coach": "प्रशिक्षक",
    "Event coordinator": "कार्यक्रम समन्वयक",
    "Health educator": "स्वास्थ्य शिक्षक",
    "Report writer": "रिपोर्ट लेखक",
    "Counsellor": "परामर्शदाता",
    "Group lead": "समूह प्रमुख",
    "Cleaning volunteer": "सफ़ाई स्वयंसेवक",
    "Tech helper": "तकनीकी सहायक",
    "Session teacher": "सत्र शिक्षक",
    "Care volunteer": "देखभाल स्वयंसेवक",
    "Driver": "चालक",
}

_DAYS_HI = {"mon": "सोमवार", "tue": "मंगलवार", "wed": "बुधवार", "thu": "गुरुवार",
            "fri": "शुक्रवार", "sat": "शनिवार", "sun": "रविवार"}
_PERIODS_HI = {"morning": "सुबह", "afternoon": "दोपहर", "evening": "शाम"}


def skill_label(skill_id: str, lang: Lang) -> str:
    """Taxonomy label for one skill id in the requested language."""
    if lang == "hi":
        return SKILL_LABELS_HI.get(skill_id, SKILLS.get(skill_id, skill_id))
    return SKILLS.get(skill_id, skill_id)


def role_label(role: str, lang: Lang) -> str:
    """Role name in the requested language; unknown roles are returned unchanged."""
    return ROLE_LABELS_HI.get(role, role) if lang == "hi" else role


def title_label(title: str, lang: Lang) -> str:
    """Task title in the requested language; unknown titles are returned unchanged."""
    return TITLE_LABELS_HI.get(title, title) if lang == "hi" else title


def slot_label(slot: str, lang: Lang) -> str:
    """'sat_morning' -> 'sat morning' (en) or 'शनिवार सुबह' (hi)."""
    if "_" not in slot:
        return slot
    day, period = slot.split("_", 1)
    if lang == "hi":
        return f"{_DAYS_HI.get(day, day)} {_PERIODS_HI.get(period, period)}"
    return f"{day} {period}"


def _role_displays(task: TaskSpec, lang: Lang) -> list[RoleDisplay]:
    return [RoleDisplay(role_id=r.id, role=role_label(r.role, lang), count=r.count,
                        required_skills=[SkillLabel(id=s, label=skill_label(s, lang))
                                         for s in r.required_skills])
            for r in task.roles]


def task_display(task: TaskSpec, lang: Lang) -> TaskDisplay:
    """Localized task header: title, slot and role names with skill labels. Ids and counts unchanged."""
    return TaskDisplay(lang=lang, title=title_label(task.title, lang), slot=slot_label(task.slot, lang),
                       roles=_role_displays(task, lang))


def _verdict(ready: bool | None, lang: Lang) -> str:
    if lang == "en":
        return "NOT PLANNED" if ready is None else ("READY" if ready else "NOT READY")
    return "अभी तय नहीं" if ready is None else ("तैयार" if ready else "तैयार नहीं")


#: Days window used by the fairness reason codes (mirrors solver/cp_sat.py's 90-day window).
RECENT_DAYS = 90


def reason_text(reason: PickReason, lang: Lang) -> str:
    """Render ONE structured pick reason in the requested language.

    Both languages are built from the same ``code`` + ``params``, so a fact cannot exist in one language
    and be missing from the other: the same skill and level, the same distance in whole km, the same
    "not picked in N days", the same newcomer count and mentor name, the same slot. That is the point -
    the Hindi view is a rendering, not a summary of a sentence the solver wrote in English.
    """
    code, p = reason.code, reason.params
    skill = str(p.get("skill", ""))
    label_en = skill_label(skill, "en").lower() if skill else ""
    label_hi = skill_label(skill, "hi") if skill else ""
    if code == "skill_confirmed":
        if lang == "en":
            return f"Has {label_en} (level {p['level']})"
        return f"{label_hi} (स्तर {p['level']} तक प्रशिक्षित)"
    if code == "skill_self_declared":
        if lang == "en":
            return f"Self-declared {label_en} (host to confirm)"
        return f"स्वयं घोषित {label_hi} (होस्ट की पुष्टि बाकी)"
    if code == "open_role":
        return "Open role: any volunteer can do it" if lang == "en" else "खुली भूमिका: कोई भी स्वयंसेवक यह काम कर सकता है"
    if code == "slot_and_distance":
        if lang == "en":
            return f"Free {str(p['slot']).replace('_', ' ')}; {float(p['distance_km']):.0f} km from the site"
        return (f"{slot_label(str(p['slot']), 'hi')} उपलब्ध; साइट से "
                f"{float(p['distance_km']):.0f} किमी दूर")
    if code == "not_picked_recently":
        days = p.get("days", RECENT_DAYS)
        return (f"Not picked in the last {days} days" if lang == "en"
                else f"पिछले {days} दिनों में नहीं चुने गए")
    if code == "picked_heavily":
        count, days = p["count"], p.get("days", RECENT_DAYS)
        if lang == "en":
            return (f"Picked {count} times in {days} days; chosen because no less-used qualified person "
                    "fitted better")
        return (f"{days} दिनों में {count} बार चुने गए; कम इस्तेमाल वाले योग्य व्यक्ति के न मिलने पर चुना गया")
    if code == "newcomer":
        drives = p["past_drives"]
        mentor = str(p.get("mentor_name", "") or "")
        if lang == "en":
            return f"Newcomer ({drives} past drives)" + (f", paired with {mentor}" if mentor else "")
        return f"नए स्वयंसेवक ({drives} पिछली ड्राइव)" + (f", {mentor} के साथ जोड़ी" if mentor else "")
    if code == "experienced_mentor":
        drives = p["past_drives"]
        return (f"Experienced ({drives} drives): can guide newcomers" if lang == "en"
                else f"अनुभवी ({drives} ड्राइव): नए साथियों का मार्गदर्शन कर सकते हैं")
    if code == "minor_guardian_consent":
        return "Under 18: guardian consent on file" if lang == "en" else "18 वर्ष से कम: अभिभावक की सहमति दर्ज है"
    if code == "promoted_from_standby":
        return "Promoted from standby" if lang == "en" else "स्टैंडबाय से पदोन्नत"
    raise ValueError(f"unknown pick reason code {code!r}")   # a new code must be rendered, not guessed


def assignment_reason_text(role_label_hi: str, slot: str, reason_codes: list[PickReason]) -> str:
    """Hindi sentence for one pick, built from the solver's structured reasons.

    A roster method that writes no codes (the baselines keep their own English narration) falls back to
    the role + slot line rather than inventing facts it does not have.
    """
    if reason_codes:
        return "; ".join(reason_text(code, "hi") for code in reason_codes) + "।"
    return f"{role_label_hi} के लिए चुने गए; {slot_label(slot, 'hi')} उपलब्ध।"


def _explanation(task: TaskSpec, roster: RosterResult, lang: Lang) -> list[str]:
    """Hindi verdict lines state the same facts as the English ones: which slots are empty, robustness, actions.

    Percentages use the identical expression as solver/ready.py and solver/cp_sat.py (``:.0%`` on the same
    float), slot numbers are the same (``#n``), and roles are named by their Hindi label rather than by internal
    role id - an id is not a fact a host can act on, and the English line names the role too.
    """
    if lang == "en":
        return list(roster.explanations)
    lines: list[str] = []
    if roster.ready:
        return ["तैयार: हर ज़रूरी भूमिका भरी है और कोई भी एक साथी निकल जाए तो भी कोई ज़रूरी जगह खाली नहीं रहेगी।"]
    roles = {r.id: r for r in task.roles}
    if roster.unfilled_slots:
        slots = ", ".join(f"{role_label(roles[s.role_id].role, 'hi') if s.role_id in roles else s.role_id} "
                          f"#{s.slot_index + 1}" for s in roster.unfilled_slots)
        lines.append(f"ये ज़रूरी जगह खाली हैं: {slots}। कोई योग्य स्वयंसेवक उपलब्ध नहीं था।")
    elif roster.unfilled_role_ids:
        names = ", ".join(role_label(next((r.role for r in task.roles if r.id == rid), rid), "hi")
                          for rid in roster.unfilled_role_ids)
        lines.append(f"{len(roster.unfilled_role_ids)} भूमिका में ज़रूरी जगह खाली है: {names}।")
    if roster.assignments and roster.metrics.robustness < 1.0:   # same condition as the English line
        percent = f"{roster.metrics.robustness:.0%}"
        lines.append(f"एक साथी के निकलने पर भरोसा {percent} है: हर भूमिका के लिए पर्याप्त स्टैंडबाय नहीं है।")
    count = len(roster.recruit_requests)
    lines.append(f"तैयार नहीं: इस ड्राइव को सुरक्षित चलाने के लिए {count} काम बाकी "
                 + ("है।" if count == 1 else "हैं।"))
    return lines


def _recruit_text(request_kind: str, role: RoleSpec | None, needed: int, skills: list[str],
                  checked: bool, slot: str, area: str, travel_km: float,
                  blocked_by: list[str] | tuple[str, ...] = ()) -> str:
    """One Hindi recruit-request sentence, built from the same facts as the English template.

    ``blocked_by`` is the standby case's list of people whose absence would leave the role uncovered; the
    names are shown here too, so the two languages carry the same information (the earlier Hindi template
    said "if this person cannot come" without saying who).
    """
    skill_text = " या ".join(skill_label(s, "hi") for s in skills) or "कोई विशेष कौशल नहीं"
    checked_text = ", केवल होस्ट द्वारा जाँचे कौशल" if checked else ""
    if request_kind == "unresolved":
        return ("इस भूमिका को ज्ञात कौशलों से नहीं जोड़ा जा सका। किसी को जोड़ने से पहले कौशल तय करें "
                "या भूमिका को सबके लिए खुला रखें।")
    if request_kind == "standby":
        label = role_label(role.role, "hi") if role is not None else ""
        who = ", ".join(str(n) for n in blocked_by)
        condition = f"अगर {who} न आ सकें" if who else "अगर ये साथी न आ सकें"
        return (f"एक ही व्यक्ति पर निर्भरता: {condition} तो {label} के लिए कोई योग्य व्यक्ति नहीं है। "
                "एक स्टैंडबाय जोड़ें।")
    return (f"{needed} जगह के लिए कोई योग्य स्वयंसेवक नहीं मिला: {skill_text} चाहिए{checked_text}, "
            f"{slot_label(slot, 'hi')} खाली, {area} से {travel_km:.0f} किमी के भीतर।")


def roster_display(task: TaskSpec, roster: RosterResult, lang: Lang) -> RosterDisplay:
    """Localized verdict, explanations, recruit asks and pick reasons for one roster."""
    roles = {r.id: r for r in task.roles}
    if lang == "en":
        return RosterDisplay(
            lang="en", ready=roster.ready, verdict=_verdict(roster.ready, "en"),
            explanations=_explanation(task, roster, "en"),
            recruit=[RecruitDisplay(role_id=q.role_id, role=q.role, needed=q.needed, text=q.reason)
                     for q in roster.recruit_requests],
            assignments=[AssignmentDisplay(volunteer_id=a.volunteer_id, role_id=a.role_id,
                                           text="; ".join(a.reasons)) for a in roster.assignments],
        )
    return RosterDisplay(
        lang="hi", ready=roster.ready, verdict=_verdict(roster.ready, "hi"),
        explanations=_explanation(task, roster, "hi"),
        recruit=[RecruitDisplay(
            role_id=q.role_id, role=role_label(q.role, "hi"), needed=q.needed,
            text=_recruit_text(q.kind, roles.get(q.role_id), q.needed, q.skills, q.checked_skill_required,
                               q.slot, q.area, q.max_travel_km, q.blocked_by_names)) for q in roster.recruit_requests],
        assignments=[AssignmentDisplay(
            volunteer_id=a.volunteer_id, role_id=a.role_id,
            text=assignment_reason_text(role_label(roles[a.role_id].role, "hi") if a.role_id in roles else a.role_id,
                                        task.slot, a.reason_codes))
            for a in roster.assignments],
    )
