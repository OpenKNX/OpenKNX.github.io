# Build OpenKNX Release Overviews for Integration in Pages, Wiki and Toolbox
# 2025 CK (OpenKNX)

import json
import logging
from github_client import GitHubClient
from release_manager import ReleaseManager
from dependency_manager import DependencyManager
from html_generator import HTMLGenerator

# names for identification of app repos:
appPrefix = "OAM-"
appSpecialNames = {"SOM-UP", "GW-REG1-Dali", "SEN-UP1-8xTH", "BEM-GardenControl"}
appExclusion = {"OAM-TestApp"}

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = GitHubClient()
release_manager = ReleaseManager(client)
dependency_manager = DependencyManager(client)
html_generator = HTMLGenerator()

def main():
    oam_repos = release_manager.fetch_app_repos(appPrefix, appSpecialNames, appExclusion)

    oam_releases_data = release_manager.fetch_apps_releases(oam_repos)
    releases_data = {
        "OpenKnxContentType": "OpenKNX/OAM/Releases",
        "OpenKnxFormatVersion": "v0.0.0-ALPHA",
        "data": oam_releases_data
    }
    with open('releases.json', 'w') as outfile:
        json.dump(releases_data, outfile, indent=4)

    # logging.info(f"OAM Release Data: {json.dumps(oam_releases_data, indent=4)}")
    oam_hardware = build_hardware_mapping(oam_releases_data)
    with open('hardware_mapping.json', 'w') as outfile:
        json.dump(oam_hardware, outfile, indent=4)
    logging.info(f"Hardware-Support: {json.dumps(oam_hardware, indent=4)}")

    html_generator.update_html(oam_releases_data)
    all_oam_dependencies = dependency_manager.fetch_all_dependencies(oam_repos)
    # Generate Dependencies Table
    html_content = html_generator.generate_html_table(all_oam_dependencies, oam_hardware)


if __name__ == "__main__":
    main()