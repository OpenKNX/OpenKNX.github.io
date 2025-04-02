import json
import os
import logging
from jinja2 import Environment, FileSystemLoader


class HTMLGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('templates'))

    def _render_template_to_file(self, template_name, output_filename, **context):
        """
        Renders a Jinja2 template to an HTML file with the provided context.

        :param template_name: Name of the template file.
        :param output_filename: Name of the output HTML file.
        :param context: Additional keyword arguments to be passed as context to the template.
        """
        template = self.env.get_template(template_name)
        html_content = template.render(**context)

        with open(output_filename, 'w', encoding='utf8') as file:
            file.write(html_content)

        return html_content

    # Erzeugt zu jedem Repo eine kleine HTML-Datei mit Ausgabe des aktuellsten Release.
    # Ein Pre-Release wird nur dann mit ausgegeben, wenn es neuer ist als das neuste Release, oder noch kein reguläres existiert
    def create_html_for_repo(self, repo_name, details):
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
        os.makedirs('releases', exist_ok=True)
        output_filename = os.path.join('releases', f'{repo_name}.html')
        self._render_template_to_file('repo_latestrelease_template.html', output_filename,
            repo_name=repo_name,
            latest_release=latest_release,
            latest_prerelease=latest_prerelease
        )

    def update_html(self, releases_data):
        logging.info("Updating HTML with release data")

        self._render_template_to_file('release_template.html','releases_list.html',
            releases_data=releases_data
        )

        # current releases htmls for apps:
        for repo, details in releases_data.items():
            self.create_html_for_repo(repo, details)

    def _is_open_device(self, device_name):
        # TODO move, this should not be part of html rendering
        return "OpenKNX" in device_name

    # TODO move, this should not be part of html rendering
    device_name_map = {
        "1TE-RP2040-SmartMF": "SmartMF-1TE-RP2040",
        "AB-SmartHouse-BinaryClock": "AB-SmartHouse-BinaryClock",
        "ABSmartHouse-BinaryInput": "AB-SmartHouse-BinaryInput",
        "AB-SmartHouse-PresenceMR16": "AB-SmartHouse-PresenceMR16",
        "AB-SmartHouse-PresenceMultiSensor": "AB-SmartHouse-PresenceMultiSensor",
        "AB-SmartHouse-PresenceWall": "AB-SmartHouse-PresenceWall",
        "AB-SmartHouse-SwitchActuator-REG6-8CH": "AB-SmartHouse-SwitchActuator-REG6-8CH",
        "AccessControl": "AB-AccessControl",
        "DeveloperBoard-JustForTesters": "?-DeveloperBoard-JustForTesters",
        "firmware_UP1-GW-RS485": "OpenKNX UP1 RS485 Gateway",
        "GardenControl": "SmartMF-GardenControl",
        "GW-UP1-IR": "?-GW-UP1-IR",
        "IP-Router-REG1-Eth": "OpenKNX-IP-Router-REG1-Eth",
        "IP-Router-REG1-LAN-TP-Base": "OpenKNX-IP-Router-REG1-LAN-TP-Base",
        "OpenKNX-PiPico-BCU-Connector": "OpenKNX PiPico BCU Connector",
        "OpenKNX-REG1-Base-V0": "OpenKNX REG1 Basismodul V0",
        "OpenKNX-REG1-BASE-V0": "OpenKNX REG1 Basismodul V0",
        "OpenKNX-REG1-Base-V1": "OpenKNX REG1 Basismodul",
        "OpenKNX-REG1-BASE-V1": "OpenKNX REG1 Basismodul",
        "OpenKNX-REG1-Basismodul": "OpenKNX REG1 Basismodul",
        "OpenKNX-REG1-Basismodul-V0": "OpenKNX REG1 Basismodul V0",
        "OpenKNX-REG1-MultiSensor": "OpenKNX REG1 Multisensor",
        "OpenKNX-UP1-8xSensor": "OpenKNX UP1 8xSensor",
        "PiPico_BCU_Connector": "OpenKNX PiPico BCU Connector",
        "PiPico-BCU-Connector": "OpenKNX PiPico BCU Connector",
        "RealPresence": "?-RealPresence",
        "RealPresence_v2.0": "?-RealPresence_v2.0",
        "REG1_BASE_V0": "OpenKNX REG1 Basismodul V0",
        "REG1_BASE_V1": "OpenKNX REG1 Basismodul",

        # oam=="GW-REG1-Dali"
        "REG1-v0": "OpenKNX REG1 Dali Gateway V0",
        "REG1-v1": "OpenKNX REG1 Dali Gateway",

        "REG2_PIPICO_V1": "OpenKNX REG2 PiPico2 V1",
        "Sensormodul-v3.0-SAMD": "SmartMF-Sensormodul-v3.0-SAMD",
        "Sensormodul-v3.1-SAMD": "SmartMF-Sensormodul-v3.1-SAMD",
        "Sensormodul-v4.x-RP2040": "SmartMF-Sensormodul-v4.x-RP2040",
        "Sensormodul-v4x-RP2040": "SmartMF-Sensormodul-v4.x-RP2040",
        "SEN-UP1-8XTH": "OpenKNX UP1 8xSensor",
        "SmartMF-1TE-RP2040": "SmartMF-1TE-RP2040",
        "Smart-MF-eHZ-Schnittstelle": "Smart-MF-eHZ-Schnittstelle",
        "Smart-MF-S0-Zaehlermodul": "Smart-MF-S0-Zaehlermodul",
        "SmartMF-Sensormodul-RP2040": "SmartMF-Sensormodul-v4.x-RP2040",
        "UP1-PM-HF": "OpenKNX UP1 Präsenzmelder+",
        "XIAO_MINI_V1": "OpenKNXiao V1",
    }

    def _hw_name_mapping(self, oam, hw_text):
        # TODO move, this should not be part of html rendering
        if oam == "SEN-UP1-8xTH" and hw_text == "firmware":
            return "OpenKNX UP1 8xSensor"
        if hw_text in self.device_name_map:
            return self.device_name_map[hw_text]
        else:
            logging.warning(f"Unknown Device Name in '{oam}': {hw_text}")
            return f"(???)-{hw_text}"

    def generate_html_table(self, oam_dependencies, oam_hardware, oam_details):
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
                devices.append(self._hw_name_mapping(oam, content_device))

        logging.debug(f"oam_data {json.dumps(oam_data, indent=4)}")

        self._create_overview_table(oam_data)

    def _create_overview_table(self, oam_data):
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
                if self._is_open_device(hw):
                    hardware_usage_count[hw] += 1
                else:
                    hardware_other_usage_count[hw] += 1

        # Sort keys by their occurrence count, then alphabetically
        modules_sorted = sorted(modules_usage_count.items(), key=lambda item: (-item[1], item[0]))
        devices_sorted = sorted(hardware_usage_count.items(), key=lambda item: (-item[1], item[0]))
        devices_other_sorted = sorted(hardware_other_usage_count.items(), key=lambda item: (-item[1], item[0]))

        logging.info(f"Modules sorted {modules_sorted}")
        logging.info(f"Device sorted {devices_sorted}  //  {devices_other_sorted}")

        self._render_template_to_file('dependencies_template.html', 'dependencies_table.html',
                                      modules_sorted=modules_sorted,
                                      devices_sorted=devices_sorted,
                                      devices_other_sorted=devices_other_sorted,
                                      oam_data=oam_data,
                                      showModules=True,
                                      showDevices=True,
                                      )

        self._render_template_to_file('dependencies_template.html', 'oam2ofm.html',
                                      modules_sorted=modules_sorted,
                                      # devices_sorted=devices_sorted,
                                      # devices_other_sorted=devices_other_sorted,
                                      oam_data=oam_data,
                                      showModules=True,
                                      showDevices=False,
                                      )

        self._render_template_to_file('dependencies_template.html', 'oam2dev.html',
                                      # modules_sorted=modules_sorted,
                                      devices_sorted=devices_sorted,
                                      devices_other_sorted=devices_other_sorted,
                                      oam_data=oam_data,
                                      showModules=False,
                                      showDevices=True,
                                      )
