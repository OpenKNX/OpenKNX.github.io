import json
import logging


class DependencyManager:
    def __init__(self, client):
        self.client = client

    def _is_openknx_dependency(self, url):
        # TODO check if the exclusion of external libs here is a clean solution
        return url.startswith("https://github.com/OpenKNX/")

    def fetch_dependencies(self, repo):
        dependencies_url = f"https://raw.githubusercontent.com/OpenKNX/{repo['name']}/{repo['default_branch']}/dependencies.txt"
        response = self.client.get_response(dependencies_url, True)
        if response is None:
            return {}
        dependencies_map = {}
        lines = response.text.splitlines()
        invalid_lines_count = 0
        incomplete_lines_count = 0

        if lines:
            for line in lines[1:]:  # Skip the header
                parts = line.split()
                if len(parts) == 4:
                    commit, branch, path, url = parts
                    # use part of https://github.com/OpenKNX/{dep_name}.git :
                    dep_name = url.split('/')[-1].replace('.git', '')
                    if self._is_openknx_dependency(url):
                        dependencies_map[dep_name] = {
                            "commit": commit,
                            "branch": branch,
                            "path": path,
                            "url": url,
                            # TODO rename to dep_name
                            "depName": dep_name
                        }
                elif len(parts) == 3:
                    commit, branch, path = parts
                    # use part after 'lib/'
                    dep_name = path.split('/')[-1]
                    # special: detect by name only
                    if dep_name.startswith('OFM-') or dep_name.startswith('OGM-') or dep_name == 'knx':
                        dependencies_map[dep_name] = {
                            "commit": commit,
                            "branch": branch,
                            "path": path,
                            "url": "https://github.com/OpenKNX/{dep_name}.git",
                            # TODO rename to dep_name
                            "depName": dep_name
                        }
                        logging.warning(f"Expect module '{dep_name}' by lib-Path only in {repo['name']}: ")
                    else:
                        logging.warning(f"Unexpected lib in incomplete dependencies.txt of {repo['name']}: {dep_name}")
                    incomplete_lines_count += 1
                else:
                    invalid_lines_count += 1

        if incomplete_lines_count > 0:
            logging.warning(f"Incomplete dependencies.txt format in {repo['name']} ({incomplete_lines_count} of {len(lines)-1} lines)")
        if invalid_lines_count > 0:
            logging.error(f"Invalid dependencies.txt format in {repo['name']} ({invalid_lines_count} of {len(lines)-1} lines)")

        return dependencies_map

    def fetch_all_dependencies(self, repos_data):
        all_dependencies = {}
        for repo in repos_data:
            dependencies = self.fetch_dependencies(repo)
            if dependencies:
                all_dependencies[repo['name']] = dependencies
        with open('dependencies.json', 'w') as outfile:
            json.dump(all_dependencies, outfile, indent=4)
        return all_dependencies
