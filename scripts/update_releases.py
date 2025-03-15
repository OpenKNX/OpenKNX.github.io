import requests
import json
import os

def fetch_releases():
    url = "https://api.github.com/orgs/OpenKNX/repos?per_page=100&type=public"
    response = requests.get(url)
    repos = response.json()
    with open('releases_urls.txt', 'w') as file:
        for repo in repos:
            file.write(f'"{repo["name"]}" {repo["releases_url"].replace("{/id}", "")}\n')

def filter_releases():
    prefix = "OAM-"
    include_list = ["SOM-UP", "GW-REG1-Dali", "SEN-UP1-8xTH", "BEM-GardenControl"]
    with open('releases_urls.txt', 'r') as infile, open('temp_releases_urls.txt', 'w') as outfile:
        for line in infile:
            if any(item in line for item in include_list) or line.startswith(f'"{prefix}'):
                outfile.write(line)
    os.replace('temp_releases_urls.txt', 'releases_urls.txt')

def fetch_release_details():
    releases_data = {}
    with open('releases_urls.txt', 'r') as file:
        for line in file:
            repo, url = line.strip().split()
            url = url.strip('"')
            repo = repo.strip('"')
            response = requests.get(url)
            releases = response.json()
            repo_data = requests.get(f"https://api.github.com/repos/OpenKNX/{repo}").json()
            releases_data[repo] = {
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
    fetch_releases()
    filter_releases()
    fetch_release_details()
    update_html()

if __name__ == "__main__":
    main()