# Definition of Data-Model
# (C) 2026 Cornelius Köpp; For Usage in OpenKNX-Project only

from dataclasses import dataclass, field


@dataclass()
class OamData:
    description: str # TODO description of model.oam_releases.OamReleasesData
    modules: list[str] # TODO = field(default_factory=list)
    modules_internal: list[str] # TODO = field(default_factory=list)
    devices: []  # set empty list for OAMs without releases # TODO check cleanup of data-collection
