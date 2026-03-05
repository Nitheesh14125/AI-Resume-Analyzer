import re
from typing import Dict, List, Set

from sqlalchemy.orm import Session

from app.models.database_models import Skill
from app.services.role_graph_service import get_all_roles, get_skill_synonyms


def normalize_skill_name(skill_name: str) -> str:
    normalized = skill_name.lower().strip()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def _build_canonical_skill_map() -> Dict[str, Set[str]]:
    synonyms = get_skill_synonyms()
    canonical_map: Dict[str, Set[str]] = {}

    for canonical, alias_list in synonyms.items():
        normalized_canonical = normalize_skill_name(canonical.replace("_", " "))
        canonical_map.setdefault(normalized_canonical, set()).add(normalized_canonical)
        for alias in alias_list:
            canonical_map[normalized_canonical].add(normalize_skill_name(alias))

    for _, role_config in get_all_roles():
        for group_config in role_config.get("skill_groups", {}).values():
            for skill_name in group_config.get("skills", {}).keys():
                normalized_skill = normalize_skill_name(skill_name.replace("_", " "))
                canonical_map.setdefault(normalized_skill, set()).add(normalized_skill)

    return canonical_map


def extract_skills_from_resume(token_set: Set[str], normalized_resume_text: str, db: Session) -> List[str]:
    canonical_skill_map = _build_canonical_skill_map()
    matched_skills = []

    for canonical_name, aliases in canonical_skill_map.items():
        for alias in aliases:
            if " " in alias and alias in normalized_resume_text:
                matched_skills.append(canonical_name)
                break
            if alias in token_set:
                matched_skills.append(canonical_name)
                break

    # Optional DB enrichment keeps compatibility with previously seeded skills.
    try:
        skills = db.query(Skill).all()
        for skill in skills:
            normalized_skill = normalize_skill_name(skill.skill_name)
            if not normalized_skill:
                continue
            if (" " in normalized_skill and normalized_skill in normalized_resume_text) or normalized_skill in token_set:
                matched_skills.append(normalized_skill)
    except Exception:
        pass

    return sorted(set(matched_skills))
