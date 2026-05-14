# Definition of Data-Model
# (C) 2026 Cornelius Köpp; For Usage in OpenKNX-Project only

from dataclasses import dataclass, field
from typing import Any


@dataclass()
class OfmData:
    full_name: str | None = field(init=False, default=None)
    name: str
    title: str | None
    icon: str | None
    ref_oam: str | None
    description: str | None
    parent_oam: str | None
    type: str | None
    prefix: str | None
    dependencies: list[str]
    icon_url: str | None = field(init=False, default=None)

    def __post_init__(self):
        self.full_name = f'{(self.parent_oam+"/" if self.parent_oam else "")}{self.name}'
        if self.icon:
            icon = self.icon.split('@')
            icon_name = icon[0]
            icon_repo_def = (icon[1] if len(icon) == 2 else "OGM-Common").split('#')
            icon_repo = icon_repo_def[0]
            if icon_repo == '.':
                icon_repo = self.full_name.split('/')[0] # for internal modules the format is OAM/module
            icon_repo_ref = icon_repo_def[1] if len(icon_repo_def)==2 else "v1"
            self.icon_url = f"https://raw.githubusercontent.com/OpenKNX/{icon_repo}/refs/heads/{icon_repo_ref}/src/Baggages/{'icons' if self.name == 'SonosNFCPlayerModule' else 'Icons'}/{icon_name}.png"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OfmData":
        return cls(
            name = data["name"],
            title = data.get("title", None),
            icon = data.get("icon", None),
            ref_oam = data.get("ref_oam", None),
            description = data.get("description", None),
            parent_oam = data.get("parent_oam", None),
            type = data.get("type", None),
            prefix = data.get("prefix", None),
            dependencies = data.get("dependencies", []),
        )
