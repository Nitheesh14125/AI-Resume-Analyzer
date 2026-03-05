import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Tuple

ROLE_GRAPH_PATH = Path(__file__).resolve().parents[2] / "data" / "role_skill_graphs.json"


@lru_cache(maxsize=1)
def load_role_graph_data() -> Dict:
    with ROLE_GRAPH_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def slugify_role_name(role_name: str) -> str:
    value = role_name.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value


def get_role_config(role_name: str) -> Tuple[str, Dict]:
    data = load_role_graph_data()
    roles = data.get("roles", {})

    requested_slug = slugify_role_name(role_name)
    if requested_slug in roles:
        return requested_slug, roles[requested_slug]

    for slug, config in roles.items():
        if config.get("display_name", "").strip().lower() == role_name.strip().lower():
            return slug, config

    supported = ", ".join(sorted(config.get("display_name", slug) for slug, config in roles.items()))
    raise ValueError(f"Role '{role_name}' not found. Supported roles: {supported}")


def get_all_roles() -> List[Tuple[str, Dict]]:
    data = load_role_graph_data()
    roles = data.get("roles", {})
    return list(roles.items())


def get_skill_synonyms() -> Dict[str, List[str]]:
    data = load_role_graph_data()
    return data.get("skill_synonyms", {})


def get_supported_role_names() -> List[str]:
    return sorted(config.get("display_name", slug) for slug, config in get_all_roles())
