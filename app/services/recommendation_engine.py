from typing import Dict, List

SKILL_PROJECT_RECOMMENDATIONS = {
    "docker": "Build and deploy a containerized application with Docker.",
    "kubernetes": "Deploy a multi-service app on Kubernetes with autoscaling.",
    "fastapi": "Build a REST API using FastAPI and JWT authentication.",
    "flask": "Create a Flask backend with role-based authorization.",
    "django": "Develop a Django app with an admin panel and APIs.",
    "api_development": "Design RESTful endpoints with proper versioning and documentation.",
    "aws": "Deploy a production-ready app on AWS using core cloud services.",
    "azure": "Deploy an app on Azure with monitoring and scaling.",
    "gcp": "Host an API and database workload on Google Cloud.",
    "ci_cd": "Set up CI/CD pipeline with automated tests and deployment.",
    "terraform": "Provision infrastructure using Terraform modules.",
    "ml_ops": "Build an MLOps pipeline for model training and deployment.",
    "sql": "Solve advanced SQL query and optimization tasks.",
    "system_design": "Design a scalable system architecture for a high-traffic use case.",
}


GROUP_LEARNING_PATHS = {
    "core": "Strengthen core programming and problem-solving foundations.",
    "core_skills": "Master role-specific core concepts before advanced tooling.",
    "frameworks": "Practice building production features with at least one major framework.",
    "databases": "Deepen database schema design, query tuning, and indexing skills.",
    "tools": "Improve developer tooling and deployment workflow proficiency.",
    "deployment": "Focus on packaging, orchestration, and reliable release workflows.",
    "cloud_platforms": "Build cloud architecture fundamentals and certification-level knowledge.",
    "security_core": "Cover incident response, monitoring, and foundational security controls.",
    "leadership": "Develop technical leadership, mentoring, and decision-making skills.",
}


def build_recommendations(role_config: Dict, missing_skills: List[str], missing_groups: List[str]) -> Dict[str, List[str]]:
    display_name = role_config.get("display_name", "this role")

    suggestions: List[str] = []
    for skill in missing_skills[:5]:
        key = skill.lower().strip().replace(" ", "_")
        suggestion = SKILL_PROJECT_RECOMMENDATIONS.get(key)
        if suggestion:
            suggestions.append(suggestion)

    if not suggestions and missing_skills:
        suggestions.append(f"Add project work covering: {', '.join(missing_skills[:5])}.")

    learning_paths = []
    for group in missing_groups:
        mapped = GROUP_LEARNING_PATHS.get(group)
        if mapped:
            learning_paths.append(mapped)

    if not learning_paths and missing_groups:
        learning_paths.append("Focus on strengthening missing skill groups with project-based practice.")

    course_recommendations = role_config.get("course_recommendations", [])
    recommended_courses = course_recommendations[:4] if len(missing_skills) >= 3 else course_recommendations[:2]

    if len(missing_skills) >= 3:
        learning_paths.append(f"Target a structured {display_name} learning path for faster progression.")

    return {
        "suggestions": list(dict.fromkeys(suggestions)),
        "learning_paths": list(dict.fromkeys(learning_paths)),
        "recommended_courses": list(dict.fromkeys(recommended_courses)),
    }
