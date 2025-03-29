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
        # "1TE-RP2040-SmartMF": "SmartMF-1TE-RP2040",
        "AB-SmartHouse-BinaryClock": "AB-SmartHouse-BinaryClock",
        "ABSmartHouse-BinaryInput": "AB-SmartHouse-BinaryInput",
        "AB-SmartHouse-PresenceMR16": "AB-SmartHouse-PresenceMR16",
        "AB-SmartHouse-PresenceMultiSensor": "AB-SmartHouse-PresenceMultiSensor",
        "AB-SmartHouse-PresenceWall": "AB-SmartHouse-PresenceWall",
        "AB-SmartHouse-SwitchActuator-REG6-8CH": "AB-SmartHouse-SwitchActuator-REG6-8CH",
        "AccessControl": "AB-AccessControl",
        "DeveloperBoard-JustForTesters": "?-DeveloperBoard-JustForTesters",
        "firmware_UP1-GW-RS485": "OpenKNX-UP1-GW-RS485",
        "GardenControl": "SmartMF-GardenControl",
        "GW-UP1-IR": "?-GW-UP1-IR",
        "IP-Router-REG1-Eth": "OpenKNX-IP-Router-REG1-Eth",
        "IP-Router-REG1-LAN-TP-Base": "OpenKNX-IP-Router-REG1-LAN-TP-Base",
        "OpenKNX-PiPico-BCU-Connector": "OpenKNX-PiPico-BCU-Connector",
        "OpenKNX-REG1-Base-V0": "OpenKNX-REG1-Base-V0",
        "OpenKNX-REG1-BASE-V0": "OpenKNX-REG1-Base-V0",
        # "OpenKNX-REG1-BASE-V0": "OpenKNX-REG1-Base-V0",
        "OpenKNX-REG1-Base-V1": "OpenKNX-REG1-Base-V1",
        "OpenKNX-REG1-BASE-V1": "OpenKNX-REG1-Base-V1",
        # "OpenKNX-REG1-BASE-V1": "OpenKNX-REG1-Base-V1",
        "OpenKNX-REG1-Basismodul": "OpenKNX-REG1-Base-V1",
        "OpenKNX-REG1-Basismodul-V0": "OpenKNX-REG1-Base-V0",
        "OpenKNX-REG1-MultiSensor": "OpenKNX-REG1-MultiSensor",
        "OpenKNX-UP1-8xSensor": "OpenKNX-SEN-UP1-8XTH",
        "PiPico_BCU_Connector": "OpenKNX-PiPico-BCU-Connector",
        "PiPico-BCU-Connector": "OpenKNX-PiPico-BCU-Connector",
        # "PiPico-BCU-Connector": "OpenKNX-PiPico-BCU-Connector",
        # "PiPico-BCU-Connector": "OpenKNX-PiPico-BCU-Connector",
        "RealPresence": "?-RealPresence",
        # "RealPresence": "?-RealPresence",
        "RealPresence_v2.0": "?-RealPresence_v2.0",
        "REG1_BASE_V0": "OpenKNX-REG1-Base-V0",
        "REG1_BASE_V1": "OpenKNX-REG1-Base-V1",
        "REG2_PIPICO_V1": "OpenKNX-REG2-PiPico",
        "Sensormodul-v3.0-SAMD": "SmartMF-Sensormodul-v3.0-SAMD",
        "Sensormodul-v3.1-SAMD": "SmartMF-Sensormodul-v3.1-SAMD",
        "Sensormodul-v4.x-RP2040": "SmartMF-Sensormodul-v4.x-RP2040",
        "Sensormodul-v4x-RP2040": "SmartMF-Sensormodul-v4.x-RP2040",
        "SEN-UP1-8XTH": "OpenKNX-SEN-UP1-8XTH",
        "SmartMF-1TE-RP2040": "SmartMF-1TE-RP2040",
        "Smart-MF-eHZ-Schnittstelle": "Smart-MF-eHZ-Schnittstelle",
        "Smart-MF-S0-Zaehlermodul": "Smart-MF-S0-Zaehlermodul",
        "SmartMF-Sensormodul-RP2040": "SmartMF-Sensormodul-v4.x-RP2040",
        "UP1-PM-HF": "OpenKNX-UP1-PM-HF",
        "XIAO_MINI_V1": "OpenKNX-XIAO_MINI_V1",
    }

    def _hw_name_mapping(self, oam, hw_text):
        # TODO move, this should not be part of html rendering
        if oam == "SEN-UP1-8xTH" and hw_text == "firmware":
            return "OpenKNX-SEN-UP1-8XTH"
        if hw_text in self.device_name_map:
            return self.device_name_map[hw_text]
        else:
            logging.warning(f"Unknown Device Name in '{oam}': {hw_text}")
            return f"(???)-{hw_text}"

    def generate_html_table(self, oam_dependencies, oam_hardware):

        # module -> usage_count
        from collections import defaultdict
        modules_usage_count = defaultdict(int)
        for dep in oam_dependencies.values():
            for key in dep.keys():
                modules_usage_count[key] += 1
        hardware_usage_count = defaultdict(int)
        hardware_other_usage_count = defaultdict(int)
        oam_hardware_normalized = {} # TODO move normalization out of html generation
        for oam, hw_list in oam_hardware.items():
            logging.info(f"Devices for {oam}: {hw_list}")
            normalized_list = oam_hardware_normalized[oam] = []
            for hw_text in hw_list:
                hw = self._hw_name_mapping(oam, hw_text)
                logging.info(f"-> Device {hw}")
                if self._is_open_device(hw):
                    hardware_usage_count[hw] += 1
                else:
                    hardware_other_usage_count[hw] += 1
                normalized_list.append(hw)

        logging.info(f"Collected Device {hardware_usage_count}")

        # Sort keys by their occurrence count, then alphabetically
        modules_sorted = sorted(modules_usage_count.items(), key=lambda item: (-item[1], item[0]))
        devices_sorted = sorted(hardware_usage_count.items(), key=lambda item: (-item[1], item[0]))
        devices_other_sorted = sorted(hardware_other_usage_count.items(), key=lambda item: (-item[1], item[0]))

        logging.info(f"Modules sorted {modules_sorted}")
        logging.info(f"Device sorted {devices_sorted}")
        logging.info(f"OAM Hardware {oam_hardware}")

        html_content = self._render_template_to_file('dependencies_template.html', 'dependencies_table.html',
            oam_dependencies=oam_dependencies,
            modules_sorted=modules_sorted,
            devices_sorted=devices_sorted,
            devices_other_sorted=devices_other_sorted,
            oam_hardware=oam_hardware_normalized
        )
        return html_content