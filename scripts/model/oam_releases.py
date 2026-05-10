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

    def is_newer(self, other):
        return other is None or self.published_at > other.published_at

@dataclass
class OamReleasesData:
    # name: str
    # url: str
    repo_url: str
    archived: bool
    description: str
    releases: list[OamReleaseData] = field(default_factory=list)
    hw_avail_open: int = 0

    def releases_extract_latest(self):
        latest_release = None
        latest_prerelease = None
        for release in self.releases:
            if not release.prerelease:
                if release.is_newer(latest_release):
                    latest_release = release
            else:
                if release.is_newer(latest_prerelease):
                    latest_prerelease = release
        return latest_prerelease, latest_release