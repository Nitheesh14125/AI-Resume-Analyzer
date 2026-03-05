from typing import Dict, List, Tuple

from app.database.db_connection import SessionLocal, engine
from app.models import database_models
from app.models.database_models import Role, RoleSkill, Skill

database_models.Base.metadata.create_all(bind=engine)

SEED_DATA: Dict[str, List[Tuple[str, float]]] = {
    "Backend Developer": [
        ("Python", 0.20),
        ("Java", 0.15),
        ("Node.js", 0.15),
        ("FastAPI", 0.10),
        ("Django", 0.10),
        ("SQL", 0.15),
        ("Docker", 0.10),
        ("Linux", 0.05),
    ],
    "Frontend Developer": [
        ("HTML", 0.15),
        ("CSS", 0.15),
        ("JavaScript", 0.20),
        ("React", 0.15),
        ("Angular", 0.10),
        ("Vue.js", 0.10),
        ("TypeScript", 0.10),
        ("Git", 0.05),
    ],
    "Full Stack Developer": [
        ("HTML", 0.10),
        ("CSS", 0.10),
        ("JavaScript", 0.15),
        ("React", 0.10),
        ("Node.js", 0.15),
        ("Python", 0.10),
        ("SQL", 0.15),
        ("Docker", 0.10),
        ("Git", 0.05),
    ],
    "Data Scientist": [
        ("Python", 0.20),
        ("Pandas", 0.20),
        ("NumPy", 0.15),
        ("Scikit-learn", 0.20),
        ("TensorFlow", 0.10),
        ("SQL", 0.10),
        ("Data Visualization", 0.05),
    ],
    "Machine Learning Engineer": [
        ("Python", 0.20),
        ("TensorFlow", 0.20),
        ("PyTorch", 0.20),
        ("Scikit-learn", 0.15),
        ("Docker", 0.10),
        ("Kubernetes", 0.10),
        ("ML Ops", 0.05),
    ],
    "DevOps Engineer": [
        ("Docker", 0.20),
        ("Kubernetes", 0.20),
        ("AWS", 0.20),
        ("Linux", 0.15),
        ("Terraform", 0.10),
        ("CI/CD", 0.10),
        ("Monitoring Tools", 0.05),
    ],
    "Cybersecurity Analyst": [
        ("Networking", 0.20),
        ("Linux", 0.15),
        ("SIEM Tools", 0.15),
        ("Penetration Testing", 0.15),
        ("Python", 0.10),
        ("Cryptography", 0.10),
        ("Security Auditing", 0.10),
        ("Incident Response", 0.05),
    ],
    "Cloud Engineer": [
        ("AWS", 0.25),
        ("Azure", 0.20),
        ("Google Cloud", 0.15),
        ("Docker", 0.15),
        ("Kubernetes", 0.15),
        ("Terraform", 0.10),
    ],
    "Mobile App Developer": [
        ("Java", 0.20),
        ("Kotlin", 0.20),
        ("Swift", 0.20),
        ("Flutter", 0.15),
        ("React Native", 0.15),
        ("Mobile UI Design", 0.10),
    ],
    "QA / Software Tester": [
        ("Manual Testing", 0.20),
        ("Automation Testing", 0.20),
        ("Selenium", 0.20),
        ("JUnit", 0.15),
        ("TestNG", 0.10),
        ("Bug Tracking Tools", 0.10),
        ("CI/CD", 0.05),
    ],
}


def seed_roles(db):
    created_count = 0
    existing_roles = {role.role_name.lower(): role for role in db.query(Role).all()}

    for role_name in SEED_DATA:
        key = role_name.lower()
        if key not in existing_roles:
            role = Role(role_name=role_name)
            db.add(role)
            db.flush()
            existing_roles[key] = role
            created_count += 1

    return existing_roles, created_count


def seed_skills(db):
    created_count = 0
    all_skills = {skill_name for skills in SEED_DATA.values() for skill_name, _ in skills}
    existing_skills = {skill.skill_name.lower(): skill for skill in db.query(Skill).all()}

    for skill_name in sorted(all_skills):
        key = skill_name.lower()
        if key not in existing_skills:
            skill = Skill(skill_name=skill_name)
            db.add(skill)
            existing_skills[key] = skill
            created_count += 1

    return created_count


def seed_role_skills(db, roles_map):
    created_count = 0
    updated_count = 0
    existing_links = {
        (role_skill.role_id, role_skill.skill_name.lower()): role_skill
        for role_skill in db.query(RoleSkill).all()
    }

    for role_name, skills in SEED_DATA.items():
        role = roles_map[role_name.lower()]
        for skill_name, weight in skills:
            key = (role.id, skill_name.lower())
            existing_link = existing_links.get(key)
            if existing_link is None:
                new_link = RoleSkill(role_id=role.id, skill_name=skill_name, weight=weight)
                db.add(new_link)
                existing_links[key] = new_link
                created_count += 1
            elif float(existing_link.weight or 0.0) != float(weight) or existing_link.skill_name != skill_name:
                existing_link.weight = weight
                existing_link.skill_name = skill_name
                updated_count += 1

    return created_count, updated_count


def main():
    db = SessionLocal()
    try:
        roles_map, roles_created = seed_roles(db)
        skills_created = seed_skills(db)
        role_skills_created, role_skills_updated = seed_role_skills(db, roles_map)
        db.commit()

        print("Seed completed successfully.")
        print(f"Roles created: {roles_created}")
        print(f"Skills created: {skills_created}")
        print(f"Role-skill mappings created: {role_skills_created}")
        print(f"Role-skill mappings updated: {role_skills_updated}")
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


if __name__ == "__main__":
    main()
