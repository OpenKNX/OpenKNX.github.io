import requests
import json
import os

def get_json_response(url):
    response = requests.get(url)
    return response.json()

def fetch_releases():
    url = "https://api.github.com/orgs/OpenKNX/repos?per_page=100&type=public"
    repos = get_json_response(url)
    return [{repo["name"]: repo["releases_url"].replace("{/id}", "")} for repo in repos]

def filter_releases(releases):
    prefix = "OAM-"
    include_list = ["SOM-UP", "GW-REG1-Dali", "SEN-UP1-8xTH", "BEM-GardenControl"]
    filtered_releases = []
    for repo in releases:
        for name, url in repo.items():
            if any(item in name for item in include_list) or name.startswith(prefix):
                filtered_releases.append({name: url})
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
    releases = fetch_releases()
    filtered_releases = filter_releases(releases)
    fetch_release_details(filtered_releases)
    update_html()

if __name__ == "__main__":
    main()