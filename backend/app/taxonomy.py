"""Skill taxonomy shared by every lane. Lane C research (R4) may propose changes; only the head edits this file."""

SKILLS: dict[str, str] = {
    "first_aid": "First aid / basic medical support",
    "health_education": "Health education and awareness",
    "hygiene_promotion": "Hygiene and sanitation promotion",
    "logistics_supplies": "Logistics, supplies and site setup",
    "driving_transport": "Driving / transport (has vehicle)",
    "dialect_awadhi": "Awadhi speaker (local-language liaison)",
    "dialect_bhojpuri": "Bhojpuri speaker (local-language liaison)",
    "hindi_fluent": "Fluent Hindi",
    "english_fluent": "Fluent English",
    "urdu_fluent": "Fluent Urdu",
    "community_mobilisation": "Community mobilisation / door-to-door outreach",
    "team_leadership": "Team leadership",
    "event_coordination": "Event coordination",
    "documentation_reporting": "Documentation, attendance and reporting",
    "photography_video": "Photography / video",
    "graphic_design": "Posters and graphic design",
    "teaching_literacy": "Teaching / literacy support",
    "counselling_support": "Counselling and psychosocial support",
    "sports_coaching": "Sports coaching",
    "tech_digital_support": "Digital and tech support",
    "food_distribution": "Cooking and food distribution",
    "tree_plantation": "Tree plantation / agriculture",
    "disaster_response": "Disaster response and rescue basics",
    "fundraising_outreach": "Fundraising and partner outreach",
}

# Roles needing any of these skills are safety-critical: only host-checked skills qualify (never self-declared).
SAFETY_CRITICAL_SKILLS = {"first_aid", "disaster_response", "driving_transport"}

SLOTS = [f"{d}_{p}" for d in ("mon", "tue", "wed", "thu", "fri", "sat", "sun") for p in ("morning", "afternoon", "evening")]

DISCLAIMER = "SYNTHETIC DATA - illustrative, no real people"
