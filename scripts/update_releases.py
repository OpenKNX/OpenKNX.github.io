# Build OpenKNX Release Overviews for Integration in Pages, Wiki and Toolbox
# 2025 CK (OpenKNX)

import json
import logging
import zipfile
from io import BytesIO
import xml.etree.ElementTree as ET

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
release_manager = ReleaseManager(client, appPrefix, appSpecialNames, appExclusion)
dependency_manager = DependencyManager(client)
html_generator = HTMLGenerator()



def download_and_extract_content_xml(zip_url):
    response = client.get_response(zip_url)
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
        oamReleases = oamData["releases"]
        if not oamReleases or not isinstance(oamReleases, list) or len(oamReleases) == 0:
            logging.warning(f"No releases found for {oamName}")
            continue
        latest_release = oamReleases[0]
        for asset in latest_release.get('assets', []):
            logging.info(f"Fetching release archive {oamName} from {asset['browser_download_url']}")
            try:
                content_xml = download_and_extract_content_xml(asset['browser_download_url'])
                if content_xml is not None:
                    hardware_info = parse_hardware_info(content_xml)
                    hardware_mapping[oamName] = hardware_info
                    break
            except ET.ParseError as e:
                logging.error(f"-> content.xml parsing error {e}")
                # Ignorieren Sie den Fehler und fahren Sie fort
        else:
            logging.warning(f"No assets found for {oamName}")
    return hardware_mapping



def main():
    oam_repos = release_manager.fetch_app_repos()

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