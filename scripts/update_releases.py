# Build OpenKNX Release Overviews for Integration in Pages, Wiki and Toolbox
# 2025 CK (OpenKNX)

import requests
import json
import os
import logging
import sys
import time

# names for identification of app repos:
appPrefix = "OAM-"
appSpecialNames = {"SOM-UP", "GW-REG1-Dali", "SEN-UP1-8xTH", "BEM-GardenControl"}

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_json_response(url):
    try:
        response = requests.get(url)
        if response.status_code == 403 and 'X-RateLimit-Reset' in response.headers:
            # Try again 5 seconds after rate limit end
            wait_time = int(response.headers['X-RateLimit-Reset']) - int(time.time())
            logging.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
            time.sleep(wait_time + 5)
            response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        # hard end on request fail to prevent missing data # TODO improve
        sys.exit(1)

def fetch_and_filter_releases():

    url = "https://api.github.com/orgs/OpenKNX/repos?per_page=1000&type=public"
    repos = get_json_response(url)
    filtered_releases = [
        repo
        for repo in repos
        if repo["name"].startswith(appPrefix) or repo["name"] in appSpecialNames
    ]
    return filtered_releases

def fetch_release_details(filtered_releases):
    releases_data = {}
    for repo in filtered_releases:
        name = repo["name"]
        url = repo["releases_url"].replace("{/id}", "")
        logging.info(f"Fetching release data {name} from {url}")
        releases = get_json_response(url.strip('"'))
        releases_data[name] = {
            "repo_url": repo["html_url"],
            "archived": repo["archived"],
            "releases": [
                {
                    "prerelease": release.get("prerelease"),
                    "tag_name": release.get("tag_name"),
                    "name": release.get("name"),
                    "published_at": release.get("published_at"),
                    "html_url": release.get("html_url")
                }
                for release in releases if isinstance(release, dict) and not release.get("draft")
            ]
        }
    with open('releases.json', 'w') as outfile:
        json.dump(releases_data, outfile, indent=4)
    return releases_data

def fetch_dependencies(repo):
    try:
        url = f"https://raw.githubusercontent.com/OpenKNX/{repo['name']}/main/dependencies.txt"
        response = requests.get(url)
        response.raise_for_status()
        dependencies = response.text.splitlines()
        return [dep.strip() for dep in dependencies if dep.strip()]
    except requests.exceptions.RequestException:
        logging.warning(f"No dependencies.txt found for {repo['name']}")
        return []

def fetch_all_dependencies(filtered_releases):
    all_dependencies = {}
    for repo in filtered_releases:
        dependencies = fetch_dependencies(repo)
        if dependencies:
            all_dependencies[repo['name']] = dependencies
    with open('dependencies.json', 'w') as outfile:
        json.dump(all_dependencies, outfile, indent=4)
    return all_dependencies

# Erzeugt zu eine kleine HTML-Datei mit Ausgabe des aktuellsten Release.
# Ein Pre-Release wird nur dann mit ausgegeben wenn es neuer ist als das neuste Release, oder noch kein reguläres existiert
def create_html_for_repo(repo_name, details):
    logging.info(f"Creating HTML for repository {repo_name}")
    os.makedirs('releases', exist_ok=True)
    with open(f'releases/{repo_name}.html', 'w') as outfile:
        outfile.write('<ul>\n')
        latest_release = None
        latest_prerelease = None
        for release in details["releases"]:
            if not release["prerelease"]:
                if latest_release is None or release["published_at"] > latest_release["published_at"]:
                    latest_release = release
            else:
                if latest_prerelease is None or release["published_at"] > latest_prerelease["published_at"]:
                    latest_prerelease = release

        if latest_release:
            outfile.write(f'<li><a href="{latest_release["html_url"]}">Neustes Release: {latest_release["name"]} ({latest_release["tag_name"]})</a></li>\n')

        if latest_prerelease and (latest_release is None or latest_prerelease["published_at"] > latest_release["published_at"]):
            outfile.write(f'<li><a href="{latest_prerelease["html_url"]}">[PRERELEASE] Neustes Pre-Release: {latest_prerelease["name"]} ({latest_prerelease["tag_name"]})</a></li>\n')

        outfile.write('</ul>\n')

def update_html(releases_data):
    logging.info("Updating HTML with release data")
    with open('releases_list.html', 'w') as outfile:
        outfile.write('<h1>Releases der OpenKNX-Applikationen</h1>\n')
        for repo, details in releases_data.items():
            create_html_for_repo(repo, details)
            outfile.write(f'<h2>{repo}</h2>\n')
            outfile.write('<ul>\n')
            for release in details["releases"]:
                prefix = "[PRERELEASE] " if release["prerelease"] else ""
                outfile.write(f'<li>{prefix}<a href="{release["html_url"]}">{release["name"]} ({release["tag_name"]})</a></li>\n')
            outfile.write('</ul>\n')

def main():
    filtered_releases = fetch_and_filter_releases()
    releases_data = fetch_release_details(filtered_releases)
    update_html(releases_data)
    all_dependencies = fetch_all_dependencies(filtered_releases)
    logging.info(f"Dependencies: {json.dumps(all_dependencies, indent=4)}")

if __name__ == "__main__":
    main()