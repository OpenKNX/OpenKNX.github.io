import os
import logging
from jinja2 import Environment, FileSystemLoader

class HTMLGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('templates'))

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
        template = self.env.get_template('repo_latestrelease_template.html')
        rendered_html = template.render(repo_name=repo_name, latest_release=latest_release, latest_prerelease=latest_prerelease)
        os.makedirs('releases', exist_ok=True)
        with open(os.path.join('releases', f'{repo_name}.html'), 'w') as outfile:
            outfile.write(rendered_html)

    def update_html(self, releases_data):
        logging.info("Updating HTML with release data")
        template = self.env.get_template('release_template.html')
        rendered_html = template.render(releases_data=releases_data)
        with open('releases_list.html', 'w') as outfile:
            outfile.write(rendered_html)
        for repo, details in releases_data.items():
            self.create_html_for_repo(repo, details)

    def generate_html_table(self, oam_dependencies, oam_hardware):
        from collections import defaultdict
        modules = set()
        modules_usage_count = defaultdict(int)
        for dep in oam_dependencies.values():
            modules.update(dep.keys())
            for key in dep.keys():
                modules_usage_count[key] += 1
        modules_sorted = sorted(modules, key=lambda k: (-modules_usage_count[k], k))
        modules_single_use = [k for k in modules_sorted if modules_usage_count[k] == 1]
        modules_multi_use = [k for k in modules_sorted if modules_usage_count[k] > 1]
        template = self.env.get_template('dependencies_template.html')
        html_content = template.render(
            oam_dependencies=oam_dependencies,
            modules_multi_use=modules_multi_use,
            modules_single_use=modules_single_use,
            key_count=modules_usage_count,
            oam_hardware=oam_hardware
        )
        with open('dependencies_table.html', 'w') as file:
            file.write(html_content)
        return html_content