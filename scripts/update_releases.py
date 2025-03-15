# Build OpenKNX Release Overviews for Integration in Pages, Wiki and Toolbox
# 2025 CK (OpenKNX)

import requests
import json
import os

def get_json_response(url):
    response = requests.get(url)
    return response.json()

def fetch_and_filter_releases():
    # TODO move repo names to separate place
    appPrefix = "OAM-"
    appSpecialNames = {"SOM-UP", "GW-REG1-Dali", "SEN-UP1-8xTH", "BEM-GardenControl"}

    url = "https://api.github.com/orgs/OpenKNX/repos?per_page=1000&type=public"
    repos = get_json_response(url)
    filtered_releases = []
    for repo in repos:
        repo_name = repo["name"]
        releases_url = repo["releases_url"].replace("{/id}", "")
        if repo_name.startswith(appPrefix) or repo_name in appSpecialNames:
            filtered_releases.append({repo_name: releases_url})
    return filtered_releases

def fetch_release_details(filtered_releases):
    releases_data = {}
    for repo in filtered_releases:
        for name, url in repo.items():
            releases = get_json_response(url.strip('"'))
            repo_data = get_json_response(f"https://api.github.com/repos/OpenKNX/{name}")
            releases_data[name] = {
                "repo_url": repo_data.get("html_url"),
                "archived": repo_data.get("archived"),
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

# Erzeugt zu eine kleine HTML-Datei mit Ausgabe des aktuellsten Release.
# Ein Pre-Release wird nur dann mit ausgegeben wenn es neuer ist als das neuste Release, oder noch kein reguläres existiert
def create_html_for_repo(repo_name, details):
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

def update_html():
    with open('releases.json', 'r') as infile, open('releases_list.html', 'w') as outfile:
        data = json.load(infile)
        outfile.write('<h1>Releases der OpenKNX-Applikationen</h1>\n')
        for repo, details in data.items():
            create_html_for_repo(repo, details)
            outfile.write(f'<h2>{repo}<h2>\n')
            outfile.write('<ul>\n')
            for release in details["releases"]:
                prefix = "[PRERELEASE] " if release["prerelease"] else ""
                outfile.write(f'<li>{prefix}<a href="{release["html_url"]}">{release["name"]} ({release["tag_name"]})</a></li>\n')
            outfile.write('</ul>\n')

def main():
    filtered_releases = fetch_and_filter_releases()
    releases_data = fetch_release_details(filtered_releases)
    update_html()

if __name__ == "__main__":
    main()