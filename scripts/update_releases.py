# Build OpenKNX Release Overviews for Integration in Pages, Wiki and Toolbox
# 2025 CK (OpenKNX)

import json
import logging
import os
import zipfile
from io import BytesIO
import xml.etree.ElementTree as ET

from github_client import GitHubClient
from release_manager import ReleaseManager
from dependency_manager import DependencyManager
from devices_helper import DeviceHelper
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
device_helper = DeviceHelper()
html_generator = HTMLGenerator(device_helper)


def download_and_extract_content_xml(zip_url):
    response = client.get_response(zip_url)
    zipfile_obj = zipfile.ZipFile(BytesIO(response.content))

    xml_content = ""
    # needs windows-path as found in zip generated by OpenKNX-Build-Process
    if 'data\\content.xml' in zipfile_obj.namelist():
        with zipfile_obj.open('data\\content.xml') as xml_file:
            xml_content = xml_file.read().decode('utf-8')
    elif 'data/content.xml' in zipfile_obj.namelist():
        with zipfile_obj.open('data/content.xml') as xml_file:
            xml_content = xml_file.read().decode('utf-8')
    else:
        logging.warning(f"No 'data\\content.xml' or 'data/content.xml' found in the archive {zip_url}")
        return None
    # quick-fix for older releases with broken XML:
    xml_str = xml_content.replace('<Products>\n</Content>\n', '</Products>\n</Content>\n')
    if xml_str != xml_content:
        logging.warning(f"Quick-Fixed broken XML in 'content.xml' found in the archive {zip_url}")

    return ET.parse(xml_str).getroot()


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
                    hardware_mapping[oamName] = parse_hardware_info(content_xml)
                    break
            except ET.ParseError as e:
                logging.error(f"-> content.xml parsing error {e}")
                # Ignorieren Sie den Fehler und fahren Sie fort
        else:
            logging.warning(f"No assets found for {oamName}")
    return hardware_mapping


def generate_oam_data(oam_dependencies, oam_hardware, oam_details):
    logging.debug(f"OAM Hardware {oam_hardware}")

    oam_data = {}
    for oam, dependencies in oam_dependencies.items():
        oam_data[oam] = {
            "description": oam_details.get(oam, {}).get("description", "(keine Kurzbeschreibung)"),
            "modules": dependencies,
            "devices": [],  # set empty list for OAMs without releases # TODO check cleanup of data-collection
        }
        if oam not in oam_details:
            logging.warning(f"Missing {oam} in oam_details, present only {oam_details.keys()}")
    for oam, oam_content_devices in oam_hardware.items():
        if oam not in oam_data:
            # TODO use same base for oam-list
            logging.warning(f"Missing {oam} in oam_data, present only {oam_data.keys()}")
            continue
        oam_data[oam]["devices"] = devices = []
        for content_device in oam_content_devices:
            # TODO move normalization out of html generation:
            devices.append(device_helper.hw_name_mapping(oam, content_device))

    logging.debug(f"oam_data {json.dumps(oam_data, indent=4)}")

    return oam_data


def main():
    oam_repos = release_manager.fetch_app_repos()

    oam_releases_data = release_manager.fetch_apps_releases(oam_repos)
    releases_data = {
        "OpenKnxContentType": "OpenKNX/OAM/Releases",
        "OpenKnxFormatVersion": "v0.1.0-ALPHA",
        "data": oam_releases_data
    }
    with open(os.path.join("docs", 'releases.json'), 'w') as outfile:
        json.dump(releases_data, outfile, indent=4)

    # logging.info(f"OAM Release Data: {json.dumps(oam_releases_data, indent=4)}")
    oam_hardware = build_hardware_mapping(oam_releases_data)
    with open('hardware_mapping.json', 'w') as outfile:
        json.dump(oam_hardware, outfile, indent=4)
    logging.info(f"Hardware-Support: {json.dumps(oam_hardware, indent=4)}")

    html_generator.update_html(oam_releases_data)
    all_oam_dependencies = dependency_manager.fetch_all_dependencies(oam_repos)

    # Generate Dependencies Table
    oam_data = generate_oam_data(all_oam_dependencies, oam_hardware, oam_releases_data)
    html_generator.update_overview_tables(oam_data)


if __name__ == "__main__":
    main()
