# Build OpenKNX Release Overviews for Integration in Pages, Wiki and Toolbox
# 2025 CK (OpenKNX)

import requests
import json
import os
import logging
import sys
import time
import zipfile
from io import BytesIO
import xml.etree.ElementTree as ET
from jinja2 import Environment, FileSystemLoader

# names for identification of app repos:
appPrefix = "OAM-"
appSpecialNames = {"SOM-UP", "GW-REG1-Dali", "SEN-UP1-8xTH", "BEM-GardenControl"}

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Jinja2
env = Environment(loader=FileSystemLoader('templates'))

def get_response(url, allowedNotFound = False):
    try:
        response = requests.get(url)
        if response.status_code == 403 and 'X-RateLimit-Reset' in response.headers:
            # Try again 5 seconds after rate limit end
            wait_time = int(response.headers['X-RateLimit-Reset']) - int(time.time())
            wait_time = max(wait_time, 0)  # Ensure wait_time is not negative
            logging.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
            time.sleep(wait_time + 5)
            response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        if allowedNotFound and response.status_code == 404:
            logging.warning(f"404 Not Found: {url}")
            return None
        error_message = f"Error fetching data from {url}: {e}"
        logging.error(error_message)
        sys.exit(error_message)

def get_json_response(url):
    return get_response(url).json()

def fetch_app_repos():
    repos_data = get_json_response("https://api.github.com/orgs/OpenKNX/repos?per_page=1000&type=public")
    app_repos_data = [
        repo
        for repo in repos_data
        if repo["name"].startswith(appPrefix) or repo["name"] in appSpecialNames
    ]
    return app_repos_data

def fetch_apps_releases(repos_data):
    releases_data = {}
    for repo in repos_data:
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
                    "html_url": release.get("html_url"),
                    "body": release.get("body"),
                    "assets": [
                        {
                            "name": asset.get("name"),
                            "updated_at": asset.get("updated_at"),
                            "browser_download_url": asset.get("browser_download_url")
                        }
                        for asset in release.get("assets") if asset.get("content_type") == "application/x-zip-compressed"
                    ]
                }
                for release in releases if isinstance(release, dict) and not release.get("draft")
            ]
        }
    return releases_data

def parse_dependencies(content):
    dependencies_map = {}
    lines = content.splitlines()
    if lines:
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
            else:
                logging.warning(f"Invalid line format {line}")
    return dependencies_map

def fetch_dependencies(repo):
    url = f"https://raw.githubusercontent.com/OpenKNX/{repo['name']}/{repo['default_branch']}/dependencies.txt"
    response = get_response(url, True)
    if response is None:
        return {}
    return parse_dependencies(response.text)

def fetch_all_dependencies(repos_data):
    all_dependencies = {}
    for repo in repos_data:
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
    with open(os.path.join('releases', f'{repo_name}.html'), 'w') as outfile:
        latest_release = None
        latest_prerelease = None
        for release in details["releases"]:
            if not release["prerelease"]:
                if latest_release is None or release["published_at"] > latest_release["published_at"]:
                    latest_release = release
            else:
                if latest_prerelease is None or release["published_at"] > latest_prerelease["published_at"]:
                    latest_prerelease = release

        outfile.write('<ul>\n')

        if latest_release:
            outfile.write(f'<li><a href="{latest_release["html_url"]}">Neustes Release: {latest_release["name"]} ({latest_release["tag_name"]})</a></li>\n')

        if latest_prerelease and (latest_release is None or latest_prerelease["published_at"] > latest_release["published_at"]):
            outfile.write(f'<li><a href="{latest_prerelease["html_url"]}">[PRERELEASE] Neustes Pre-Release: {latest_prerelease["name"]} ({latest_prerelease["tag_name"]})</a></li>\n')

        outfile.write('</ul>\n')

def update_html(releases_data):
    logging.info("Updating HTML with release data")
    template = env.get_template('release_template.html')
    rendered_html = template.render(releases_data=releases_data)
    with open('releases_list.html', 'w') as outfile:
        outfile.write(rendered_html)
    # current releases htmls for apps:
    for repo, details in releases_data.items():
        create_html_for_repo(repo, details)

def generate_html_table(dependencies):
    all_keys = set()
    for dep in dependencies.values():
        all_keys.update(dep.keys())

    all_keys = sorted(all_keys, key=lambda k: sum(1 for dep in dependencies.values() if k in dep), reverse=True)

    template = env.get_template('dependencies_template.html')
    html_content = template.render(dependencies=dependencies, all_keys=all_keys)
    with open('dependencies_table.html', 'w') as file:
        file.write(html_content)
    return html_content


def download_and_extract_content_xml(zip_url):
    response = get_response(zip_url)
    zipfile_obj = zipfile.ZipFile(BytesIO(response.content))
    # needs windows-path as found in zip generated by OpenKNX-Build-Process
    if 'data\\content.xml' in zipfile_obj.namelist():
        with zipfile_obj.open('data\\content.xml') as xml_file:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            return root
    else:
        logging.warning(f"No 'data\\content.xml' found in the archive {zip_url}")
        return None

def parse_hardware_info(content_xml):
    products = content_xml.find('Products')
    hardware = []
    for product in products:
        hardware.append(product.get('Name'))
    return hardware

def build_hardware_mapping(releases_data):
    hardware_mapping = {}
    for oamName, oamData in releases_data.items():
        logging.info(f"Fetching hardware data for {oamName}")
        oamReleases = oamData["releases"]
        if not oamReleases or not isinstance(oamReleases, list):
            logging.warning(f"No releases found for {oamName}")
            continue
        latest_release = oamReleases[0]
        if latest_release:
            for asset in latest_release.get('assets', []):
                logging.info(f"-> Fetching release archive {asset['browser_download_url']}")
                content_xml = download_and_extract_content_xml(asset['browser_download_url'])
                if content_xml is not None:
                    hardware_info = parse_hardware_info(content_xml)
                    hardware_mapping[oamName] = hardware_info
                    break
    return hardware_mapping


def main():
    oam_repos = fetch_app_repos()

    oam_releases_data = fetch_apps_releases(oam_repos)
    releases_data = {
        "OpenKnxContentType": "OpenKNX/OAM/Releases",
        "OpenKnxFormatVersion": "v0.0.0-ALPHA",
        "data": oam_releases_data
    }
    with open('releases.json', 'w') as outfile:
        json.dump(releases_data, outfile, indent=4)

    update_html(oam_releases_data)
    all_oam_dependencies = fetch_all_dependencies(oam_repos)
    # Generate Dependencies Table
    html_content = generate_html_table(all_oam_dependencies)

    # logging.info(f"OAM Release Data: {json.dumps(oam_releases_data, indent=4)}")
    hardware_mapping = build_hardware_mapping(oam_releases_data)
    with open('hardware_mapping.json', 'w') as outfile:
        json.dump(hardware_mapping, outfile, indent=4)
    logging.info(f"Hardware-Support: {json.dumps(hardware_mapping, indent=4)}")


if __name__ == "__main__":
    main()