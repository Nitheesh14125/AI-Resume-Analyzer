import re
from typing import Dict, List, Set

from sqlalchemy.orm import Session

from app.services.recommendation_engine import build_recommendations
from app.services.role_graph_service import get_all_roles, get_role_config
from app.services.skill_extractor import normalize_skill_name


def _score_role(role_config: Dict, normalized_resume_skills: Set[str]) -> Dict:
    skill_groups = role_config.get("skill_groups", {})

    total_score = 0.0
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    missing_groups: List[str] = []
    group_breakdown: List[Dict[str, str | float]] = []

    for group_name, group_config in skill_groups.items():
        group_weight = float(group_config.get("weight", 0))
        skills = group_config.get("skills", {})

        group_score = 0.0
        total_group_skill_points = float(sum(float(points) for points in skills.values()))

        for skill_name, points in skills.items():
            normalized_skill = normalize_skill_name(skill_name.replace("_", " "))
            readable_skill = skill_name.replace("_", " ").title()

            if normalized_skill in normalized_resume_skills:
                matched_skills.append(readable_skill)
                group_score += float(points)
            else:
                missing_skills.append(readable_skill)

        if total_group_skill_points > 0 and group_weight > 0:
            normalized_group_score = min(group_weight, (group_score / total_group_skill_points) * group_weight)
        else:
            normalized_group_score = 0.0

        if normalized_group_score < group_weight * 0.45 and skills:
            missing_groups.append(group_name)

        total_score += normalized_group_score
        group_breakdown.append(
            {
                "group": group_name,
                "group_weight": group_weight,
                "group_score": round(normalized_group_score, 2),
            }
        )

    total_score = round(min(100.0, total_score), 2)
    matched_skills = sorted(set(matched_skills))

    # Prioritize missing skills with higher weighted contribution.
    weighted_missing = []
    for group_name, group_config in skill_groups.items():
        group_weight = float(group_config.get("weight", 0))
        skills = group_config.get("skills", {})
        total_group_skill_points = float(sum(float(points) for points in skills.values())) or 1.0

        for skill_name, points in skills.items():
            readable_skill = skill_name.replace("_", " ").title()
            if readable_skill in matched_skills:
                continue
            contribution = (float(points) / total_group_skill_points) * group_weight
            weighted_missing.append((readable_skill, contribution))

    weighted_missing.sort(key=lambda item: item[1], reverse=True)
    missing_skills = [skill for skill, _ in weighted_missing[:8]]

    recommendations = build_recommendations(
        role_config=role_config,
        missing_skills=missing_skills,
        missing_groups=missing_groups,
    )

    primary_suggestion = (
        recommendations["suggestions"][0]
        if recommendations["suggestions"]
        else "Keep strengthening core role skills with project-based experience."
    )

    return {
        "role_name": role_config.get("display_name", "Unknown"),
        "resume_score": total_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestion": primary_suggestion,
        "suggestions": recommendations["suggestions"],
        "learning_paths": recommendations["learning_paths"],
        "recommended_courses": recommendations["recommended_courses"],
        "group_breakdown": group_breakdown,
    }


def _infer_experience_years(resume_text: str | None) -> int:
    if not resume_text:
        return 0
    lower_text = resume_text.lower()
    lines = [line.strip() for line in lower_text.splitlines() if line.strip()]

    ignore_markers = {
        "boxing",
        "training",
        "champion",
        "cgpa",
        "semester",
        "academic",
        "education",
        "school",
        "college",
        "university",
        "hobby",
        "extracurricular",
    }

    strict_patterns = [
        r"experience\s*[:\-]?\s*(\d{1,2}(?:\.\d+)?)\s*\+?\s*(?:years|year|yrs|yr)\b",
        r"(\d{1,2}(?:\.\d+)?)\s*\+?\s*(?:years|year|yrs|yr)\s+(?:of\s+)?(?:professional\s+|work\s+)?experience\b",
        r"(?:professional|work)\s+experience\s*(?:of)?\s*(\d{1,2}(?:\.\d+)?)\s*\+?\s*(?:years|year|yrs|yr)\b",
    ]

    loose_pattern = r"(?<![\d.])(\d{1,2}(?:\.\d+)?)\s*\+?\s*(?:years|year|yrs|yr)\b"

    candidates: List[float] = []
    strict_candidates: List[float] = []

    for line in lines:
        if any(marker in line for marker in ignore_markers):
            continue

        for pattern in strict_patterns:
            for match in re.findall(pattern, line):
                try:
                    value = float(match)
                except ValueError:
                    continue
                strict_candidates.append(value)

        # Use loose matches only when line context clearly refers to experience.
        if "experience" in line or "worked" in line or "employment" in line:
            for match in re.findall(loose_pattern, line):
                try:
                    value = float(match)
                except ValueError:
                    continue
                candidates.append(value)

    selected = strict_candidates or candidates
    if not selected:
        return 0

    max_years = max(selected)
    if max_years < 0 or max_years > 50:
        return 0

    # Conservative rounding prevents inflated experience labels.
    return int(max_years)


def _role_maturity_multiplier(role_name: str, experience_years: int, matched_count: int) -> float:
    name = role_name.strip().lower()
    if experience_years >= 2 or matched_count >= 7:
        if name in {"fresher", "intern"}:
            return 0.74
    if experience_years >= 4:
        if name in {"junior software engineer", "fresher", "intern"}:
            return 0.82
    if experience_years == 0 and matched_count <= 4:
        if name in {"fresher", "intern"}:
            return 1.08
    return 1.0


def calculate_resume_score(
    role_name: str,
    resume_skills: List[str],
    db: Session | None = None,
    resume_text: str | None = None,
) -> Dict[str, str | float | List[str] | List[Dict]]:
    _, role_config = get_role_config(role_name)
    normalized_resume_skills = {normalize_skill_name(skill) for skill in resume_skills}
    result = _score_role(role_config=role_config, normalized_resume_skills=normalized_resume_skills)
    result["detected_resume_skills"] = sorted(set(skill.title() for skill in normalized_resume_skills))

    required_role_skills = []
    for group_config in role_config.get("skill_groups", {}).values():
        required_role_skills.extend(skill.replace("_", " ").title() for skill in group_config.get("skills", {}).keys())
    result["required_role_skills"] = sorted(set(required_role_skills))

    return result


def calculate_best_role_score(
    resume_skills: List[str],
    db: Session | None = None,
    resume_text: str | None = None,
) -> Dict[str, str | float | List[str] | List[Dict[str, str | float]]]:
    normalized_resume_skills = {normalize_skill_name(skill) for skill in resume_skills}
    experience_years = _infer_experience_years(resume_text)

    role_results = []
    for _, role_config in get_all_roles():
        result = _score_role(role_config=role_config, normalized_resume_skills=normalized_resume_skills)
        multiplier = _role_maturity_multiplier(
            role_name=result["role_name"],
            experience_years=experience_years,
            matched_count=len(result["matched_skills"]),
        )
        adjusted_score = round(float(result["resume_score"]) * multiplier, 2)
        result["resume_score"] = min(100.0, adjusted_score)
        role_results.append(result)

    role_results.sort(key=lambda item: float(item["resume_score"]), reverse=True)
    if not role_results:
        raise ValueError("No role skill graph configured.")

    best_result = role_results[0]
    role_scores = [{"role_name": str(item["role_name"]), "score": float(item["resume_score"])} for item in role_results]

    top_role_insights = []
    for item in role_results[:3]:
        top_role_insights.append(
            {
                "role_name": item["role_name"],
                "score": item["resume_score"],
                "matched_skills": item["matched_skills"],
                "missing_skills": item["missing_skills"],
                "suggestions": item["suggestions"],
                "recommended_courses": item["recommended_courses"],
            }
        )

    return {
        **best_result,
        "role_scores": role_scores,
        "top_role_insights": top_role_insights,
        "detected_resume_skills": sorted(set(skill.title() for skill in normalized_resume_skills)),
        "profile_experience_years": experience_years,
    }
