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

def get_response(url, allowedNotFound = False):
    try:
        response = requests.get(url)
        if response.status_code == 403 and 'X-RateLimit-Reset' in response.headers:
            # Try again 5 seconds after rate limit end
            wait_time = int(response.headers['X-RateLimit-Reset']) - int(time.time())
            logging.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
            time.sleep(wait_time + 5)
            response = requests.get(url)
        response.raise_for_status()
        return response
    # TODO combine both exceptions
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404 and not allowedNotFound:
            logging.warning(f"404 Not Found: {url}")
            return None
        logging.error(f"Error fetching data from {url}: {e}")
        # hard end on request fail to prevent missing data # TODO improve
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        # hard end on request fail to prevent missing data # TODO improve
        sys.exit(1)

def get_json_response(url):
    return get_response(url).json()

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
        releases = get_json_response(url)
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

def parse_dependencies(content):
    dependencies_map = {}
    lines = content.splitlines()
    for line in lines[1:]:  # Skip the header
        parts = line.split()
        if len(parts) == 4:
            commit, branch, path, url = parts
            repo_name = url.split('/')[-1].replace('.git', '')  # Ableiten des Repo-Namens aus der URL
            dependencies_map[repo_name] = {
                "commit": commit,
                "branch": branch,
                "path": path,
                "url": url,
                "depName": repo_name
            }
    return dependencies_map

def fetch_dependencies(repo):
    url = f"https://raw.githubusercontent.com/OpenKNX/{repo['name']}/{repo['default_branch']}/dependencies.txt"
    response = get_response(url, true)
    if response is None:
        return {}
    return parse_dependencies(response.text)

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

def generate_html_table(dependencies):
    all_keys = set()
    for dep in dependencies.values():
        all_keys.update(dep.keys())

    all_keys = sorted(all_keys, key=lambda k: sum(1 for dep in dependencies.values() if k in dep), reverse=True)

    html_content = '<html>\n<head>\n<title>Dependencies Table</title>\n<link rel="stylesheet" href="css/table_header_rotate.css">\n</head>\n<body>\n'
    html_content += '<table>\n'

    html_content += '<thead><tr><th>Dependency</th>'
    for key in all_keys:
        html_content += f'<th class="rotate"><div><span>{key}</span></div></th>'
    html_content += '</tr></thead>\n'

    html_content += '<tbody>\n'
    for dep_name, dep_details in dependencies.items():
        html_content += f'<tr><th>{dep_name}</th>'
        for key in all_keys:
            if key in dep_details:
                html_content += '<td>X</td>'
            else:
                html_content += '<td></td>'
        html_content += '</tr>\n'
    html_content += '</tbody>\n'

    html_content += '</table>\n</body>\n</html>'
    # Write to HTML file
    with open('dependencies_table.html', 'w') as file:
        file.write(html_content)
    return html_content

def main():
    filtered_releases = fetch_and_filter_releases()
    releases_data = fetch_release_details(filtered_releases)
    update_html(releases_data)
    all_dependencies = fetch_all_dependencies(filtered_releases)
    # Generate Dependencies Table
    html_content = generate_html_table(all_dependencies)

if __name__ == "__main__":
    main()