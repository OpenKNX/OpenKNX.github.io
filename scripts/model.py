# Definition of Data-Model
# (C) 2026 Cornelius Köpp; For Usage in OpenKNX-Project only

from dataclasses import dataclass, field


@dataclass()
class ReleaseAsset:
    name: str
    size: str
    digest: str
    updated_at: str
    browser_download_url: str

@dataclass
class OamReleaseData:
    prerelease: bool
    tag_name: str
    name: str
    published_at: str # TODO replace with better type
    html_url: str
    body: str
    assets: list[ReleaseAsset] = field(default_factory=list)

@dataclass
class OamReleasesData:
    # name: str
    # url: str
    repo_url: str
    archived: bool
    description: str
    releases: list[OamReleaseData] = field(default_factory=list)
    hw_avail_open: int = 0
    # TODO add methode to extract latest_prerelease, latest_release