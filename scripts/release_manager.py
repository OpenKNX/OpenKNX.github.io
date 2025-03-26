from github_client import GitHubClient
import logging

class ReleaseManager:
    def __init__(self, client):
        self.client = client

    def fetch_app_repos(self, app_prefix, app_special_names, app_exclusion):
        repos_data = self.client.get_json_response(f"{self.client.base_url}/orgs/OpenKNX/repos?per_page=1000&type=public")
        app_repos_data = [
            repo for repo in repos_data
            if (repo["name"].startswith(app_prefix) or repo["name"] in app_special_names) and repo["name"] not in app_exclusion
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