# Data-Model Helper
# (C) 2026 Cornelius Köpp; For Usage in OpenKNX-Project only

from dataclasses import is_dataclass, asdict

# allow dumping of mixed object-structure to json
def ensure_json_convertable(o):
    if is_dataclass(o):
        return asdict(o)
    if isinstance(o, dict):
        return {
            key: ensure_json_convertable(value)
            for key, value in o.items()
        }
    if isinstance(o, list):
        return [
            ensure_json_convertable(value)
            for value in o
        ]
    return o
