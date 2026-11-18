"""Deterministic SYNTHETIC volunteers and tasks for the demo and the evaluation.

Provenance (docs/research/R4-up-realism.md, Lane C):
- District centroid coordinates come from docs/research/up_districts.json (open-admin-data, retrieved 2026-11-18).
- Block names are the ones printed on official district websites (R4 lines 6-9, 24); Bharohiya is skipped (19-vs-20 conflict).
- Positions are SYNTHETIC: random offsets around the district centroid; they are not real block locations.
- Names are invented first names plus an initial; no real person, phone or email is used. Ages, skills, availability and
  pick history are design assumptions (R4 marks volunteer distributions as INFERENCE).
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from ..schemas import RoleSpec, TaskSpec, Volunteer

_DISTRICTS_JSON = Path(__file__).resolve().parents[3] / "docs" / "research" / "up_districts.json"
_FALLBACK = {"Lucknow": (26.843, 80.907), "Kanpur Dehat": (26.437, 79.862), "Varanasi": (25.318, 82.974), "Gorakhpur": (26.760, 83.373)}

BLOCKS = {
    "Kanpur Dehat": ["Akbarpur", "Maitha", "Sarvankheda", "Jhinjhak", "Rasulabad", "Amraudha", "Malasa", "Sandalpur", "Rajpur"],
    "Lucknow": ["Chinhat", "Gosaiganj", "Kakori", "Mall", "Malihabad", "Mohanlalganj", "Sarojini Nagar"],
    "Varanasi": ["Kashi Vidyapeeth", "Cholapur", "Arajiline", "Chiraigaon", "Harhua", "Pindra", "Sevapuri", "Badagaon"],
    "Gorakhpur": ["Pipraich", "Khorabar", "Bhathat", "Sardarnagar", "Bansgaon", "Gola", "Barhalganj"],
}
# Regional language skill by district (R4: Awadhi in Awadh, Bhojpuri in the east). INFERENCE, labelled.
_DIALECT = {"Kanpur Dehat": "dialect_awadhi", "Lucknow": "dialect_awadhi", "Varanasi": "dialect_bhojpuri", "Gorakhpur": "dialect_bhojpuri"}

_FIRST = ["Aarav", "Asha", "Bhavna", "Chirag", "Deepika", "Faiz", "Gaurav", "Heena", "Ishaan", "Jyoti", "Kabir", "Lata",
          "Manav", "Naina", "Om", "Pooja", "Rahul", "Ritika", "Sahil", "Sana", "Tanvi", "Uday", "Vani", "Yash", "Zoya",
          "Ankit", "Divya", "Imran", "Kavya", "Mohit", "Neha", "Pranav", "Ruchi", "Saurabh", "Shreya", "Tarun", "Usha",
          "Vikas", "Anjali", "Rohit"]
_FEMALE = {"Asha", "Bhavna", "Deepika", "Heena", "Jyoti", "Lata", "Naina", "Pooja", "Ritika", "Sana", "Tanvi", "Vani", "Zoya",
           "Divya", "Kavya", "Neha", "Ruchi", "Shreya", "Usha", "Anjali"}

# Common skills (weights) - first aid, dialects and disaster response are deliberately scarce.
_COMMON = {
    "hindi_fluent": 10, "community_mobilisation": 6, "logistics_supplies": 6, "documentation_reporting": 5, "event_coordination": 4,
    "team_leadership": 3, "photography_video": 4, "graphic_design": 3, "teaching_literacy": 5, "health_education": 3,
    "hygiene_promotion": 3, "food_distribution": 4, "tree_plantation": 4, "sports_coaching": 3, "tech_digital_support": 4,
    "english_fluent": 4, "counselling_support": 2, "fundraising_outreach": 2, "urdu_fluent": 2, "driving_transport": 2,
}
_SLOT_POOL = ["sat_morning", "sat_morning", "sun_morning", "sun_morning", "sat_afternoon", "sun_afternoon", "sat_evening", "wed_evening"]


def _centroids() -> dict[str, tuple[float, float]]:
    try:
        data = json.loads(_DISTRICTS_JSON.read_text(encoding="utf-8"))
        found = {d["name"]: (float(d["lat"]), float(d["lon"])) for d in data["districts"] if d["name"] in BLOCKS}
        if len(found) == len(BLOCKS):
            return found
    except (OSError, KeyError, ValueError):
        pass
    return dict(_FALLBACK)


def _offset(rng: random.Random, lat: float, lon: float, max_deg: float) -> tuple[float, float]:
    return round(lat + rng.uniform(-max_deg, max_deg), 4), round(lon + rng.uniform(-max_deg, max_deg), 4)


def make_volunteers(n: int = 80, seed: int = 7) -> list[Volunteer]:
    rng = random.Random(seed)
    cent = _centroids()
    districts = ["Kanpur Dehat"] * 18 + ["Lucknow"] * 18 + ["Varanasi"] * 12 + ["Gorakhpur"] * 12
    districts = (districts * ((n // len(districts)) + 1))[:n]
    vols: list[Volunteer] = []
    skills_pool, weights = list(_COMMON), list(_COMMON.values())
    for i in range(n):
        d = districts[i]
        lat, lon = _offset(rng, *cent[d], 0.12)
        first = _FIRST[i % len(_FIRST)]
        age = rng.choice([16, 17] if i % 8 == 3 else list(range(18, 30)))
        skills: dict[str, int] = {}
        for s in rng.choices(skills_pool, weights=weights, k=rng.randint(3, 5)):
            skills[s] = rng.choice([1, 1, 2, 2, 3])
        if rng.random() < 0.45:
            skills[_DIALECT[d]] = rng.choice([2, 3])
        langs = ["hi"] + (["en"] if "english_fluent" in skills else []) + (["ur"] if "urdu_fluent" in skills else [])
        past = rng.choice([0, 0, 1, 2, 3, 4, 5, 6, 8, 11])
        vols.append(Volunteer(
            id=f"v-{i + 1:03d}", display_name=f"{first} {chr(65 + rng.randrange(26))}.", age=age,
            gender="F" if first in _FEMALE else "M", district=d, block=rng.choice(BLOCKS[d]), lat=lat, lon=lon,
            skills=skills, self_declared_skills=[], languages=langs,
            available_slots=sorted(set(rng.choices(_SLOT_POOL, k=rng.randint(3, 5)))),
            has_vehicle="driving_transport" in skills, past_drives=past,
            times_picked_last_90d=(rng.choice([4, 5, 7]) if past >= 6 and rng.random() < 0.6 else rng.choice([0, 0, 1, 2])),
            guardian_consent=(None if age >= 18 else rng.random() < 0.6), synthetic=True,
        ))
    _scarce(vols, rng)
    _ensure_feasible(vols, make_tasks(seed), rng)
    return vols


SCARCE_TASKS = {"task-04", "task-05"}  # deliberately left short of eligible people to test honest 'unfilled' reporting


def _ensure_feasible(vols: list[Volunteer], tasks: list[TaskSpec], rng: random.Random) -> None:
    """Design rule (documented in PROJECT_REPORT): on 8 of 10 tasks every role gets at least count+1 eligible candidates
    so methods are compared on decisions, not on impossible inputs. We only ADD the task slot and one required skill to
    nearby adult volunteers who are not yet eligible; nobody is moved. SCARCE_TASKS are left as generated."""
    from ..solver.metrics import distance_km, is_eligible  # local import: solver depends on schemas only
    for task in tasks:
        if task.id in SCARCE_TASKS:
            continue
        for role in task.roles:
            near = [v for v in vols if v.age >= 18 and distance_km(task, v) <= task.max_travel_km and not is_eligible(v, role, task)]
            rng.shuffle(near)
            while sum(is_eligible(v, role, task) for v in vols) < role.count + 1 and near:
                v = near.pop()
                if task.slot not in v.available_slots:
                    v.available_slots = sorted(set(v.available_slots) | {task.slot})
                if role.required_skills and not any(v.skills.get(s, 0) >= role.min_level for s in role.required_skills):
                    v.skills[role.required_skills[0]] = max(role.min_level, 2)
                v.has_vehicle = "driving_transport" in v.skills


def _scarce(vols: list[Volunteer], rng: random.Random) -> None:
    """Make first aid and disaster response scarce but present, plus a few self-declared (unconfirmed) skills."""
    adults = [v for v in vols if v.age >= 18]
    for v in rng.sample(adults, 12):           # 12 confirmed first-aiders of 80 (mixed levels): scarce
        v.skills["first_aid"] = rng.choice([1, 2, 3])
    for v in rng.sample(adults, 6):            # 6 disaster-response trained
        v.skills["disaster_response"] = rng.choice([2, 3])
    for v in rng.sample([v for v in vols if "first_aid" not in v.skills], 3):
        v.self_declared_skills.append("first_aid")   # claims a skill a host has not confirmed
    for v in vols:                              # every district has at least one weekend-morning person per dialect
        v.has_vehicle = "driving_transport" in v.skills


def _role(i: int, role: str, skills: list[str], count: int = 1, priority: str = "must", min_level: int = 1,
          needs_experienced: bool = False) -> RoleSpec:
    return RoleSpec(id=f"role-{i:02d}", role=role, count=count, required_skills=skills, min_level=min_level,
                    priority=priority, needs_experienced=needs_experienced, confidence="high")  # type: ignore[arg-type]


def make_tasks(seed: int = 7) -> list[TaskSpec]:
    """10 labelled test tasks with ground-truth roles (the eval set). Varied, some hard, some easy for a greedy baseline."""
    rng = random.Random(seed + 1000)
    cent = _centroids()
    spec = [
        ("task-01", "Water and hygiene camp", "Kanpur Dehat", "Akbarpur", "sat_morning", 25, True, "hi",
         "गाँव स्तर पर शनिवार सुबह स्वच्छ पेयजल और हाथ धोने की जागरूकता शिविर। लगभग 120 लोग आएँगे। पोस्टर, प्राथमिक उपचार, सामान और स्थानीय बोली में बात करने वाले चाहिए।",
         [("Team lead", ["team_leadership", "event_coordination"], 1, "must", 1, False),
          ("Local-language liaison", ["dialect_awadhi"], 1, "must", 2, False),
          ("First-aid support", ["first_aid"], 1, "must", 1, True),
          ("Logistics and supplies", ["logistics_supplies", "driving_transport"], 1, "must", 1, False),
          ("Hygiene educator", ["hygiene_promotion", "health_education"], 1, "must", 1, False),
          ("Documentation", ["documentation_reporting", "photography_video"], 1, "should", 1, False)]),
        ("task-02", "Blood donation camp", "Lucknow", "Chinhat", "sun_morning", 25, False, "en",
         "Sunday morning blood donation camp in Chinhat. Need trained first aid, people to register donors and mobilise the neighbourhood, and someone to manage supplies.",
         [("First-aid support", ["first_aid"], 2, "must", 1, True),
          ("Donor registration", ["documentation_reporting", "tech_digital_support"], 1, "must", 1, False),
          ("Community mobiliser", ["community_mobilisation"], 2, "must", 1, False),
          ("Supplies", ["logistics_supplies"], 1, "should", 1, False)]),
        ("task-03", "Tree plantation drive", "Gorakhpur", "Pipraich", "sun_morning", 25, True, "hinglish",
         "Sunday ko Pipraich mein tree plantation drive hai, 200 paudhe lagane hain. Planting team, saplings ki logistics aur photos chahiye.",
         [("Planting team", ["tree_plantation"], 2, "must", 1, False),
          ("Sapling logistics", ["logistics_supplies", "driving_transport"], 1, "must", 1, False),
          ("Photos and report", ["photography_video", "documentation_reporting"], 1, "should", 1, False)]),
        ("task-04", "Evening literacy class", "Varanasi", "Cholapur", "sat_afternoon", 25, True, "hi",
         "शनिवार दोपहर चोलापुर में बच्चों के लिए पढ़ाई की कक्षा। दो पढ़ाने वाले और भोजपुरी में अभिभावकों से बात करने वाला चाहिए।",
         [("Teacher", ["teaching_literacy"], 2, "must", 1, False),
          ("Parent liaison (Bhojpuri)", ["dialect_bhojpuri"], 1, "must", 2, False),
          ("Attendance and records", ["documentation_reporting"], 1, "should", 1, False)]),
        ("task-05", "Flood relief distribution", "Gorakhpur", "Gola", "sat_morning", 30, False, "en",
         "Flood relief distribution in Gola on Saturday morning. Adults only. Need disaster-response trained volunteers, first aid, a driver with supplies and food distribution, and a Bhojpuri speaker.",
         [("Relief lead", ["disaster_response"], 1, "must", 2, True),
          ("First-aid support", ["first_aid"], 1, "must", 1, False),
          ("Driver and supplies", ["driving_transport"], 1, "must", 1, False),
          ("Food distribution", ["food_distribution"], 2, "must", 1, False),
          ("Local liaison (Bhojpuri)", ["dialect_bhojpuri"], 1, "must", 1, False)]),
        ("task-06", "Block sports day", "Lucknow", "Kakori", "sun_afternoon", 25, True, "hinglish",
         "Kakori block sports day Sunday afternoon. Do coaches, ek first aid volunteer aur event coordinator chahiye.",
         [("Coach", ["sports_coaching"], 2, "must", 1, False),
          ("First-aid support", ["first_aid"], 1, "must", 1, False),
          ("Event coordinator", ["event_coordination", "team_leadership"], 1, "must", 1, False)]),
        ("task-07", "Health awareness camp", "Varanasi", "Kashi Vidyapeeth", "sun_morning", 25, True, "hi",
         "रविवार सुबह स्वास्थ्य जागरूकता शिविर। स्वास्थ्य शिक्षा, प्राथमिक उपचार, भोजपुरी में बात करने वाला और रिपोर्ट लिखने वाला चाहिए। परामर्श हो सके तो अच्छा।",
         [("Health educator", ["health_education"], 1, "must", 1, False),
          ("First-aid support", ["first_aid"], 1, "must", 1, False),
          ("Local liaison (Bhojpuri)", ["dialect_bhojpuri"], 1, "must", 1, False),
          ("Report writer", ["documentation_reporting"], 1, "must", 1, False),
          ("Counsellor", ["counselling_support"], 1, "should", 1, False)]),
        ("task-08", "Cleanliness drive", "Kanpur Dehat", "Maitha", "sun_morning", 25, True, "en",
         "Sunday morning cleanliness drive in Maitha market. Anyone can help; one person should lead the group.",
         [("Group lead", ["team_leadership", "event_coordination"], 1, "must", 1, False),
          ("Cleaning volunteer", [], 4, "must", 1, False)]),
        ("task-09", "Digital literacy for elders", "Lucknow", "Mohanlalganj", "sat_afternoon", 25, True, "en",
         "Saturday afternoon digital literacy session: help elders use UPI and DigiLocker. Need two tech helpers and one teacher.",
         [("Tech helper", ["tech_digital_support"], 2, "must", 1, False),
          ("Session teacher", ["teaching_literacy"], 1, "must", 1, False)]),
        ("task-10", "Elderly care visits", "Kanpur Dehat", "Rasulabad", "sat_morning", 25, True, "hi",
         "शनिवार सुबह रसूलाबाद में बुज़ुर्गों से मिलने जाना है। परामर्श या स्वास्थ्य जानकारी वाला, अवधी बोलने वाला और गाड़ी वाला चाहिए।",
         [("Care volunteer", ["counselling_support", "health_education"], 1, "must", 1, False),
          ("Local-language liaison", ["dialect_awadhi"], 1, "must", 1, False),
          ("Driver", ["driving_transport"], 1, "must", 1, False)]),
    ]
    tasks: list[TaskSpec] = []
    for tid, title, d, block, slot, km, minors, lang, brief, roles in spec:
        lat, lon = _offset(rng, *cent[d], 0.06)
        tasks.append(TaskSpec(
            id=tid, title=title, brief_text=brief, language=lang, slot=slot, district=d, block=block, lat=lat, lon=lon,  # type: ignore[arg-type]
            team_size=sum(r[2] for r in roles), max_travel_km=km, allow_minors=minors,
            roles=[_role(i + 1, *r) for i, r in enumerate(roles)], synthetic=True))
    return tasks
