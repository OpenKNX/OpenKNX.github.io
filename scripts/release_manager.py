# Collect OAM-Repos, Releases-Info and Release-Archive-Assets
# (C) 2025 Cornelius Köpp; For Usage in OpenKNX-Project only

import logging


class ReleaseManager:
    def __init__(self, client, app_prefix, app_special_names, app_exclusion):
        self.client = client
        self.app_prefix = app_prefix
        self.app_special_names = app_special_names
        self.app_exclusion = app_exclusion

    def _check_include_repo(self, repo):
        rn = repo["name"]
        return (rn.startswith(self.app_prefix) or rn in self.app_special_names) and rn not in self.app_exclusion

    def fetch_app_repos(self):
        """
        Read the info for all public Application Repos (selected by Name) from API and return full data as List.

        :return: list of structured repo data
        """
        repos_url = f"{self.client.base_url}/orgs/OpenKNX/repos?per_page=1000&type=public"
        repos_data = self.client.get_json_response(repos_url)
        app_repos_data = [
            repo
            for repo in repos_data
            if self._check_include_repo(repo)
        ]
        return app_repos_data

    def fetch_apps_releases(self, repos_data):
        releases_data = {}
        for repo in repos_data:
            name = repo["name"]
            url = repo["releases_url"].replace("{/id}", "")
            logging.info(f"Fetching release data {name} from {url}")
            releases = self.client.get_json_response(url)
            releases_data[name] = {
                "repo_url": repo["html_url"],
                "archived": repo["archived"],
                "description": repo["description"],
                "releases": [
                    {
                        "prerelease": release.get("prerelease"),
                        "tag_name": release.get("tag_name"),
                        "name": release.get("name"),
                        "published_at": release.get("published_at"),
                        "html_url": release.get("html_url"),
                        "body": release.get("body"),
                        "assets": [
                            {
                                "name": asset.get("name"),
                                "updated_at": asset.get("updated_at"),
                                "browser_download_url": asset.get("browser_download_url")
                            }
                            for asset in release.get("assets") if asset.get("name").endswith(".zip")
                        ]
                    }
                    for release in releases if isinstance(release, dict) and not release.get("draft")
                ]
            }
        return releases_data
