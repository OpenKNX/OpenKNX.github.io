import json
import os
import logging
from jinja2 import Environment, FileSystemLoader

from devices_helper import DeviceHelper


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

    def create_html_for_repo(self, repo_name, details):
        """
        Erzeugt zu jedem Repo eine kleine HTML-Datei mit Ausgabe des aktuellsten Release.
        Ein Pre-Release wird nur dann mit ausgegeben, wenn es neuer ist als das neuste Release, oder noch kein reguläres existiert

        :param repo_name:
        :param details:
        :return:
        """
        logging.info(f"Creating HTML for repository {repo_name}")
        latest_release = None
        latest_prerelease = None
        for release in details["releases"]:
            if not release["prerelease"]:
                if latest_release is None or release["published_at"] > latest_release["published_at"]:
                    latest_release = release
            else:
                if latest_prerelease is None or release["published_at"] > latest_prerelease["published_at"]:
                    latest_prerelease = release

        # create release info for this repo
        output_filename = os.path.join('releases', f'{repo_name}.html')
        self._render_template_to_file('repo_latestrelease_template.html', output_filename,
                                      repo_name=repo_name,
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
            self.create_html_for_repo(repo, details)


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

        self._render_template_to_file('dependencies_template.html', 'dependencies_table.html',
                                      title="OpenKNX-Applikationen, enthaltene Module und unterstützte Geräte",
                                      modules_sorted=modules_sorted,
                                      devices_sorted=devices_sorted,
                                      devices_other_sorted=devices_other_sorted,
                                      oam_data=oam_data,
                                      showModules=True,
                                      showDevices=True,
                                      )

        self._render_template_to_file('dependencies_template.html', 'oam2ofm.html',
                                      title="OpenKNX-Applikationen und enthaltene Module",
                                      modules_sorted=modules_sorted,
                                      # devices_sorted=devices_sorted,
                                      # devices_other_sorted=devices_other_sorted,
                                      oam_data=oam_data,
                                      showModules=True,
                                      showDevices=False,
                                      )

        self._render_template_to_file('dependencies_template.html', 'oam2dev.html',
                                      # modules_sorted=modules_sorted,
                                      title="OpenKNX-Applikationen und unterstützte Geräte",
                                      devices_sorted=devices_sorted,
                                      devices_other_sorted=devices_other_sorted,
                                      oam_data=oam_data,
                                      showModules=False,
                                      showDevices=True,
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
                                          )
