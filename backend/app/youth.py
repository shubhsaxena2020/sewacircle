"""Youth-side matching: rank community projects (drives) for one young person.

Eligibility rules (age, 18+ projects, distance beyond twice the travel limit) run first and are never traded off against the score; the score that follows is a transparent
weighted sum (skills 40, availability 25, distance 20, interests 15) so every percentage can be explained line by line.
Safety-critical roles (first aid, driving, disaster response) still need a host to check the skill, so a self-declared
skill is shown as "host check needed", never as a qualification.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .schemas import RoleSpec, TaskSpec
from .solver.metrics import haversine_km
from .taxonomy import SKILLS

MIN_AGE = 16
WEIGHTS = {"skills": 40, "availability": 25, "distance": 20, "interests": 15}

# Interest chips -> words that appear in project titles and briefs (English and Hindi).
INTERESTS: dict[str, list[str]] = {
    "health": ["health", "medical", "blood", "hygiene", "स्वास्थ्य", "स्वच्छ"],
    "environment": ["tree", "plantation", "clean", "water", "पेयजल", "पौध"],
    "education": ["literacy", "teaching", "school", "digital", "साक्षरता", "शिक्षा"],
    "disaster_relief": ["flood", "relief", "disaster", "बाढ़", "राहत"],
    "sports": ["sports", "खेल"],
    "food": ["food", "ration", "भोजन"],
    "elderly_care": ["elderly", "care", "बुज़ुर्ग"],
}

SLOT_LABEL = {"sat_morning": "Saturday morning", "sun_morning": "Sunday morning", "sat_afternoon": "Saturday afternoon",
              "sun_afternoon": "Sunday afternoon", "sat_evening": "Saturday evening", "wed_evening": "Wednesday evening"}
SLOT_LABEL_HI = {"sat_morning": "शनिवार सुबह", "sun_morning": "रविवार सुबह", "sat_afternoon": "शनिवार दोपहर",
                 "sun_afternoon": "रविवार दोपहर", "sat_evening": "शनिवार शाम", "wed_evening": "बुधवार शाम"}


class YouthProfile(BaseModel):
    age: int = Field(ge=10, le=40)
    lat: float
    lon: float
    district: str = ""
    skills: list[str] = Field(default_factory=list, description="taxonomy ids the person declares")
    interests: list[str] = Field(default_factory=list, description="keys of INTERESTS")
    available_slots: list[str] = Field(default_factory=list)


class ProjectMatch(BaseModel):
    task_id: str
    title: str
    district: str
    block: str
    slot: str
    distance_km: float
    percent: int
    parts: dict[str, int]
    best_role: str | None
    host_check_needed: bool
    reasons: list[str]
    improve: str | None


class Excluded(BaseModel):
    task_id: str
    title: str
    reason: str


class YouthResult(BaseModel):
    matches: list[ProjectMatch]
    excluded: list[Excluded]
    weights: dict[str, int]
    synthetic: bool = True


def _skill_fit(task: TaskSpec, skills: set[str]) -> tuple[float, RoleSpec | None, bool]:
    """Best role for this person: 1.0 for a matching ordinary role, 0.6 for a safety role (host check needed)."""
    best: tuple[float, RoleSpec | None, bool] = (0.0, None, False)
    for role in task.roles:
        if not role.required_skills and not role.safety_critical:
            score, check = 0.7, False          # open role: anyone can do it, a matching skill still ranks higher
        elif not skills & set(role.required_skills):
            continue
        else:
            score, check = (0.6, True) if role.safety_critical else (1.0, False)
        if score > best[0]:
            best = (score, role, check)
    return best


def _interest_fit(task: TaskSpec, interests: list[str]) -> tuple[float, str | None]:
    text = f"{task.title} {task.brief_text}".lower()
    for key in interests:
        if any(word.lower() in text for word in INTERESTS.get(key, [])):
            return 1.0, key
    return 0.0, None


def recommend(profile: YouthProfile, tasks: list[TaskSpec], lang: Literal["en", "hi"] = "en", top: int = 10) -> YouthResult:
    hi = lang == "hi"
    skills = set(profile.skills)
    matches: list[ProjectMatch] = []
    excluded: list[Excluded] = []
    for t in tasks:
        # 1) mandatory eligibility, before any score
        if profile.age < MIN_AGE:
            excluded.append(Excluded(task_id=t.id, title=t.title, reason=f"न्यूनतम आयु {MIN_AGE} वर्ष" if hi else f"Minimum age is {MIN_AGE}"))
            continue
        if profile.age < 18 and not t.allow_minors:
            excluded.append(Excluded(task_id=t.id, title=t.title, reason="यह अभियान केवल 18+ के लिए है" if hi else "This project is for 18+ only"))
            continue
        d = haversine_km(profile.lat, profile.lon, t.lat, t.lon)
        if d > 2 * t.max_travel_km:
            excluded.append(Excluded(task_id=t.id, title=t.title, reason=(f"{d:.0f} किमी दूर, यात्रा सीमा {t.max_travel_km:.0f} किमी से बहुत अधिक" if hi else f"{d:.0f} km away, far beyond the {t.max_travel_km:.0f} km travel limit")))
            continue
        # 2) explainable score
        s_fit, role, check = _skill_fit(t, skills)
        avail = 1.0 if t.slot in profile.available_slots else 0.0
        dist = max(0.0, 1 - 0.5 * d / t.max_travel_km) if d <= t.max_travel_km else max(0.0, 0.5 - (d - t.max_travel_km) / t.max_travel_km)
        i_fit, interest = _interest_fit(t, profile.interests)
        parts = {"skills": round(WEIGHTS["skills"] * s_fit), "availability": round(WEIGHTS["availability"] * avail),
                 "distance": round(WEIGHTS["distance"] * dist), "interests": round(WEIGHTS["interests"] * i_fit)}
        reasons: list[str] = []
        if role and not role.required_skills:
            reasons.append(f"भूमिका '{role.role}' सभी के लिए खुली है" if hi else f"The role '{role.role}' is open to everyone")
        elif role:
            label = SKILLS.get(next(iter(skills & set(role.required_skills))), "")
            reasons.append((f"आपका कौशल '{label}' भूमिका '{role.role}' से मेल खाता है" if hi else f"Your skill '{label}' fits the role '{role.role}'"))
        else:
            reasons.append("आपके किसी कौशल से कोई भूमिका मेल नहीं खाती" if hi else "None of your skills matches a role yet")
        slot_label = (SLOT_LABEL_HI if hi else SLOT_LABEL).get(t.slot, t.slot)
        reasons.append((f"आप {slot_label} उपलब्ध हैं" if avail else f"यह {slot_label} है, जब आप उपलब्ध नहीं") if hi
                       else (f"You are free on {slot_label}" if avail else f"It runs on {slot_label}, when you are not free"))
        reasons.append((f"{d:.0f} किमी दूर (सीमा {t.max_travel_km:.0f} किमी)" if hi else f"{d:.0f} km away (travel limit {t.max_travel_km:.0f} km)"))
        if interest:
            reasons.append((f"आपकी रुचि से मेल: {interest.replace('_', ' ')}" if hi else f"Matches your interest: {interest.replace('_', ' ')}"))
        if check:
            reasons.append("सुरक्षा भूमिका: होस्ट आपके कौशल की जाँच करेगा" if hi else "Safety role: a host must check this skill before you are seated")
        improve = None
        if not role:
            want = sorted({s for r in t.roles if not r.safety_critical for s in r.required_skills})
            if want:
                improve = (f"'{SKILLS.get(want[0], want[0])}' जोड़ने से यह मेल बढ़ेगा" if hi else f"Adding '{SKILLS.get(want[0], want[0])}' would raise this match")
        elif not avail:
            improve = (f"{slot_label} खाली रखने से यह मेल बढ़ेगा" if hi else f"Being free on {slot_label} would raise this match")
        matches.append(ProjectMatch(task_id=t.id, title=t.title, district=t.district, block=t.block, slot=t.slot,
                                    distance_km=round(d, 1), percent=sum(parts.values()), parts=parts,
                                    best_role=role.role if role else None, host_check_needed=check, reasons=reasons, improve=improve))
    matches.sort(key=lambda m: (-m.percent, m.distance_km))
    return YouthResult(matches=matches[:top], excluded=excluded, weights=WEIGHTS)
