# Collect OAM-Repos, Releases-Info and Release-Archive-Assets
# (C) 2025-2026 Cornelius Köpp; For Usage in OpenKNX-Project only

import logging

from model.oam_data import OamRepo
from model.oam_releases import ReleaseAsset, OamReleaseData, OamReleasesData


class ReleaseManager:
    def __init__(self, client, app_prefix, app_special_names, app_exclusion):
        self.client = client
        self.app_prefix = app_prefix
        self.app_special_names = app_special_names
        self.app_exclusion = app_exclusion

    def _check_include_repo(self, repo: dict[str, str]) -> bool:
        rn = repo["name"]
        return (rn.startswith(self.app_prefix) or rn in self.app_special_names) and rn not in self.app_exclusion

    def fetch_app_repos(self) -> list[OamRepo]:
        """
        Read the info for all public Application Repos (selected by Name) from API and return full data as List.

        :return: list of structured repo data
        """
        repos_data = self.client.get_org_repos()
        app_repos_data = [
            OamRepo(
                name = repo["name"],
                updated_at = repo["updated_at"],
                pushed_at = repo["pushed_at"],
                releases_url = repo["releases_url"],
                repo_url = repo["html_url"],
                archived = repo["archived"],
                description = repo["description"],
                default_branch = repo["default_branch"],
            )
            for repo in repos_data
            if self._check_include_repo(repo)
        ]
        return app_repos_data

    def fetch_apps_releases(self, repos_data: list[OamRepo]) -> dict[str, OamReleasesData]:
        releases_data = {}
        for repo in repos_data:
            name = repo.name
            url = repo.releases_url.replace("{/id}", "") # TODO define function?
            logging.info(f"Fetching release data {name} from {url}")
            releases = self.client.get_json_response(url)
            releases_data[name] = OamReleasesData(
                repo_url = repo.repo_url,
                archived = repo.archived,
                description = repo.description,
                releases = [
                    OamReleaseData(
                        prerelease = release.get("prerelease"),
                        tag_name = release.get("tag_name"),
                        name = release.get("name"),
                        published_at = release.get("published_at"),
                        html_url = release.get("html_url"),
                        body = release.get("body"),
                        assets = [
                            ReleaseAsset(
                                name = asset.get("name"),
                                size = asset.get("size"),
                                digest = asset.get("digest"),
                                updated_at = asset.get("updated_at"),
                                browser_download_url = asset.get("browser_download_url")
                            )
                            for asset in release.get("assets") if asset.get("name").endswith(".zip")
                        ]
                    )
                    for release in releases if isinstance(release, dict) and not release.get("draft")
                ]
            )
        return releases_data
