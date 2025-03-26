import json
import logging

class DependencyManager:
    def __init__(self, client):
        self.client = client

    def fetch_dependencies(self, repo):
        url = f"https://raw.githubusercontent.com/OpenKNX/{repo['name']}/{repo['default_branch']}/dependencies.txt"
        response = self.client.get_response(url, True)
        if response is None:
            return {}
        dependencies_map = {}
        lines = response.text.splitlines()
        if lines:
            for line in lines[1:]:
                parts = line.split()
                if len(parts) == 4:
                    commit, branch, path, url = parts
                    dep_name = url.split('/')[-1].replace('.git', '')
                    if url.startswith("https://github.com/OpenKNX/"):
                        dependencies_map[dep_name] = {
                            "commit": commit,
                            "branch": branch,
                            "path": path,
                            "url": url,
                            "dep_name": dep_name
                        }
                else:
                    logging.warning(f"Invalid dependencies.txt format in {repo['name']} line '{line}'")
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