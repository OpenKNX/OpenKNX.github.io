# Quick and Dirty Wrapper for Access to GitHub API with Minimalistic Error Handling
# (C) 2025 Cornelius Köpp; For Usage in OpenKNX-Project only

import logging
import sys
import time

import requests


class GitHubClient:
    def __init__(self, base_url="https://api.github.com"):
        self.base_url = base_url

    def get_response(self, url, allowed_not_found=False):
        response = None
        try:
            response = requests.get(url)
            if response.status_code == 403 and 'X-RateLimit-Reset' in response.headers:
                # Try again 5 seconds after rate limit end
                wait_time = max(0, int(response.headers['X-RateLimit-Reset']) - int(time.time()))
                logging.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
                time.sleep(wait_time + 5)
                response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if allowed_not_found and response is not None and response.status_code == 404:
                logging.warning(f"404 Not Found: {url}")
                return None
            error_message = f"Error fetching data from {url}: {e}"
            logging.error(error_message)
            sys.exit(error_message)

    def get_json_response(self, url):
        return self.get_response(url).json()
