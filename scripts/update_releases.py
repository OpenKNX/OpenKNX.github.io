import requests
import json
import os

def get_json_response(url):
    response = requests.get(url)
    return response.json()

def fetch_and_filter_releases():
    url = "https://api.github.com/orgs/OpenKNX/repos?per_page=100&type=public"
    repos = get_json_response(url)
    prefix = "OAM-"
    include_set = {"SOM-UP", "GW-REG1-Dali", "SEN-UP1-8xTH", "BEM-GardenControl"}
    filtered_releases = []
    for repo in repos:
        repo_name = repo["name"]
        releases_url = repo["releases_url"].replace("{/id}", "")
        if repo_name.startswith(prefix) or repo_name in include_set:
            filtered_releases.append({repo_name: releases_url})
    return filtered_releases

def fetch_release_details(filtered_releases):
    releases_data = {}
    for repo in filtered_releases:
        for name, url in repo.items():
            releases = get_json_response(url.strip('"'))
            repo_data = get_json_response(f"https://api.github.com/repos/OpenKNX/{name.strip('"')}")
            releases_data[name] = {
                "repo_url": repo_data.get("html_url"),
                "isDeprecated": repo_data.get("archived"),
                "releases": [
                    {
                        "isPrerelease": release.get("prerelease"),
                        "tag": release.get("tag_name"),
                        "name": release.get("name"),
                        "archivUrl": release.get("html_url")
                    }
                    for release in releases
                ]
            }
    with open('releases.json', 'w') as outfile:
        json.dump(releases_data, outfile, indent=4)

def update_html():
    with open('releases.json', 'r') as infile, open('releases_list.html', 'w') as outfile:
        data = json.load(infile)
        outfile.write('<ul>\n')
        for repo, details in data.items():
            outfile.write(f'<li><strong>{repo}</strong><ul>\n')
            for release in details["releases"]:
                outfile.write(f'<li><a href="{release["archivUrl"]}">{release["name"]} ({release["tag"]})</a></li>\n')
            outfile.write('</ul></li>\n')
        outfile.write('</ul>\n')

def main():
    filtered_releases = fetch_and_filter_releases()
    fetch_release_details(filtered_releases)
    update_html()

if __name__ == "__main__":
    main()