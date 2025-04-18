# Create HTML-Files from Collected Data Using Jinja2-Templates
# (C) 2025 Cornelius Köpp; For Usage in OpenKNX-Project only

import json
import os
import logging
import re

from jinja2 import Environment, FileSystemLoader

from devices_helper import DeviceHelper


def to_device_pathname(device_name):
    umlauts = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss', 'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue'}
    for umlaut, replacement in umlauts.items():
        device_name = device_name.replace(umlaut, replacement)

    # allow alphanumeric, _ and - characters only
    return re.sub(r'[^A-Za-z0-9_-]', '_', device_name)


class HTMLGenerator:
    def __init__(self, device_helper):
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.device_helper = device_helper

    def _render_template_to_file(self, template_name, output_filename, **context):
        """
        Renders a Jinja2 template to an HTML file with the provided context.

        :param template_name: Name of the template file.
        :param output_filename: Name of the output HTML file.
        :param context: Additional keyword arguments to be passed as context to the template.
        """
        template = self.env.get_template(template_name)
        html_content = template.render(**context)

        with open(os.path.join("docs", output_filename), 'w', encoding='utf8') as file:
            file.write(html_content)

        return html_content

    def create_html_for_repo(self, oam, oam_releases):
        """
        Erzeugt zu jedem Repo eine kleine HTML-Datei mit Ausgabe des aktuellsten Release.
        Ein Pre-Release wird nur dann mit ausgegeben, wenn es neuer ist als das neuste Release, oder noch kein reguläres existiert

        :param oam:
        :param oam_releases:
        :return:
        """
        logging.info(f"Creating HTML for repository {oam}")
        latest_release = None
        latest_prerelease = None
        for release in oam_releases:
            if not release["prerelease"]:
                if latest_release is None or release["published_at"] > latest_release["published_at"]:
                    latest_release = release
            else:
                if latest_prerelease is None or release["published_at"] > latest_prerelease["published_at"]:
                    latest_prerelease = release

        # create release info for this repo
        output_filename = os.path.join('oam', oam, 'releases_latest.html')
        os.makedirs(os.path.join("docs", 'oam', oam), exist_ok=True)
        self._render_template_to_file('repo_latestrelease_template.html', output_filename,
                                      repo_name=oam,
                                      latest_release=latest_release,
                                      latest_prerelease=latest_prerelease
                                      )

    def update_html(self, releases_data):
        logging.info("Updating HTML with release data")

        self._render_template_to_file('release_template.html', 'releases_list.html',
                                      releases_data=releases_data
                                      )

        # current releases htmls for apps:
        for repo, details in releases_data.items():
            self.create_html_for_repo(repo, details["releases"])

    def update_overview_tables(self, oam_data):
        # module,devices -> usage_count
        from collections import defaultdict
        modules_usage_count = defaultdict(int)
        hardware_usage_count = defaultdict(int)
        hardware_other_usage_count = defaultdict(int)
        for oam_details in oam_data.values():
            for module in oam_details["modules"].keys():
                modules_usage_count[module] += 1
        for oam, oam_details in oam_data.items():
            hw_list = oam_details["devices"]
            logging.debug(f"Devices for {oam}: {hw_list}")
            for hw in hw_list:
                if self.device_helper.is_open_device(hw):
                    hardware_usage_count[hw] += 1
                else:
                    hardware_other_usage_count[hw] += 1

        # Sort keys by their occurrence count, then alphabetically
        modules_sorted = sorted(modules_usage_count.items(), key=lambda item: (-item[1], item[0]))
        devices_sorted = sorted(hardware_usage_count.items(), key=lambda item: (-item[1], item[0]))
        devices_other_sorted = sorted(hardware_other_usage_count.items(), key=lambda item: (-item[1], item[0]))

        logging.debug(f"Modules sorted: {modules_sorted}")
        logging.debug(f"Devices (OpenKNX) sorted: {devices_sorted}")
        logging.debug(f"Devices (other) sorted: {devices_other_sorted}")

        render_configs = [
            (True, True, "dependencies_table.html", "OpenKNX-Applikationen, enthaltene Module und unterstützte Geräte"),
            (True, False, "oam2ofm.html", "OpenKNX-Applikationen und enthaltene Module"),
            (False, True, "oam2dev.html", "OpenKNX-Applikationen und unterstützte Geräte"),
        ]
        for showModules, showDevices, output_file, title in render_configs:
            self._render_template_to_file(
                'dependencies_template.html',
                output_file,
                title=title,
                modules_sorted=modules_sorted if showModules else [],
                devices_sorted=devices_sorted if showDevices else [],
                devices_other_sorted=devices_other_sorted if showDevices else [],
                oam_data=oam_data,
                showModules=showModules,
                showDevices=showDevices,
            )

        for oamName, oam_details in oam_data.items():
            path = os.path.join("oam", oamName)
            os.makedirs(os.path.join("docs", path), exist_ok=True)
            file = os.path.join(path, "index.html")
            logging.debug(f"Create OAM Overview in {file}")
            self._render_template_to_file('oam_overview.html', file,
                                          oamName=oamName,
                                          oam_details=oam_details,
                                          # same order as in large overview table. TODO Reversed might be better for modules
                                          modules_sorted=modules_sorted,
                                          devices_sorted=devices_sorted,
                                          devices_other_sorted=devices_other_sorted,
                                          function_device_to_pathname=to_device_pathname,
                                          )

        for ofmName, ofm_usage_count in modules_sorted:

            from collections import defaultdict
            dev_usage_count = defaultdict(int)
            for oam, oam_details in oam_data.items():
                # use supported devices of all oams with this module:
                if ofmName in oam_details["modules"]:
                    for dev in oam_details["devices"]:
                        dev_usage_count[dev] += 1
            devs_sorted = sorted(dev_usage_count.items(), key=lambda item: (-item[1], item[0]))

            path = os.path.join("ofm", ofmName)
            os.makedirs(os.path.join("docs", path), exist_ok=True)
            file = os.path.join(path, "index.html")
            logging.debug(f"Create OFM Overview in {file}")
            self._render_template_to_file('ofm_overview.html', file,
                                          ofmName=ofmName,
                                          oam_data=oam_data,
                                          # TODO devices_data
                                          devs_sorted=dev_usage_count,
                                          devices_sorted=devices_sorted,
                                          devices_other_sorted=devices_other_sorted,
                                          function_device_to_pathname=to_device_pathname,
                                          )

        for device_name, usageCount in devices_sorted:

            from collections import defaultdict
            ofm_usage_count = defaultdict(int)
            for oam, oam_details in oam_data.items():
                # use supported devices of all oams with this module:
                if device_name in oam_details["devices"]:
                    for ofm in oam_details["modules"]:
                        ofm_usage_count[ofm] += 1
            devs_sorted = sorted(ofm_usage_count.items(), key=lambda item: (-item[1], item[0]))
            # TODO use device-id?
            path = os.path.join("devices", to_device_pathname(device_name))
            os.makedirs(os.path.join("docs", path), exist_ok=True)
            file = os.path.join(path, "index.html")
            logging.debug(f"Create Device Overview in {file}")
            self._render_template_to_file('device_overview.html', file,
                                          name=device_name,
                                          oam_data=oam_data,
                                          ofm_sorted=devs_sorted
                                          )

            oam_data_of_device = {
                oam_name: oam_details
                for oam_name, oam_details in oam_data.items() if device_name in oam_details['devices']
            }
            modules_of_device = {
                module
                for oam_details in oam_data_of_device.values()
                for module in oam_details["modules"]
            }
            modules_sorted_of_device = [module for module in modules_sorted if module[0] in modules_of_device]
            self._render_template_to_file('dependencies_template.html',
                                          os.path.join("devices", to_device_pathname(device_name), 'functions.html'),
                                          title=f"OpenKNX-Applikationen und enthaltene Module für {device_name}",
                                          modules_sorted=modules_sorted_of_device,
                                          # devices_sorted=devices_sorted,
                                          # devices_other_sorted=devices_other_sorted,
                                          oam_data=oam_data_of_device,
                                          showModules=True,
                                          showDevices=False,
                                          )
