# Definition of Data-Model
# (C) 2026 Cornelius Köpp; For Usage in OpenKNX-Project only

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta


@dataclass()
class OamData:
    description: str # TODO description of model.oam_releases.OamReleasesData
    modules: list[str] # TODO = field(default_factory=list)
    modules_internal: list[str] # TODO = field(default_factory=list)
    devices: []  # set empty list for OAMs without releases # TODO check cleanup of data-collection

@dataclass()
class OamRepo:
    name: str # TODO type
    updated_at: str # TODO type
    pushed_at: str # TODO type
    releases_url: str # TODO cleanup?
    repo_url: str
    archived: bool
    description: str
    default_branch: str

    def changed_within(self, delta: timedelta, now: datetime) -> bool:
       return (
               (now - datetime.strptime(self.updated_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)) <= delta
               or
               (now - datetime.strptime(self.pushed_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)) <= delta
       )

    @classmethod
    def get_updated_within(cls, oam_repos: list["OamRepo"], delta: timedelta) -> dict[str, str]:
        now = datetime.now(timezone.utc)
        return {
            repo.name: repo.updated_at
            for repo in oam_repos
            if repo.changed_within(delta, now)
        }

