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

    def generate_html_table(self, oam_dependencies, oam_hardware):

        # module -> usage_count
        from collections import defaultdict
        modules_usage_count = defaultdict(int)
        for dep in oam_dependencies.values():
            for key in dep.keys():
                modules_usage_count[key] += 1
        hardware_usage_count = defaultdict(int)
        hardware_other_usage_count = defaultdict(int)
        for hw_list in oam_hardware.values():
            logging.info(f"Devices {hw_list}")
            for hw in hw_list:
                logging.info(f"-> Device {hw}")
                if self._is_open_device(hw):
                    hardware_usage_count[hw] += 1
                else:
                    hardware_other_usage_count[hw] += 1

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
            oam_hardware=oam_hardware
        )
        return html_content