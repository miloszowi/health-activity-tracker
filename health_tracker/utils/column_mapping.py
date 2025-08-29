import os

def load_mapping(env_var: str) -> dict:
    raw = os.getenv(env_var, "")
    mapping = {}
    for part in raw.split(","):
        if not part.strip():
            continue
        col, field = part.split(":")
        mapping[col.strip()] = field.strip()

    return mapping