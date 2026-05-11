# Definition of Data-Model
# (C) 2026 Cornelius Köpp; For Usage in OpenKNX-Project only

from dataclasses import dataclass, field


@dataclass()
class OamDependencies:
    commit: str
    branch: str
    path: str
    url: str
    depName: str # TODO rename to dep_name
