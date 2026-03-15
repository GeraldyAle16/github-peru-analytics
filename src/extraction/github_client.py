import os
import time
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

class GitHubClient:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}" if self.token else None,
            "Accept": "application/vnd.github.v3+json"
        }
        self.headers = {k: v for k, v in self.headers.items() if v is not None}

    def check_rate_limit(self) -> dict:
        response = requests.get(f"{self.base_url}/rate_limit", headers=self.headers)
        return response.json()

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
    def make_request(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)

        remaining = int(response.headers.get("X-RateLimit-Remaining", 100))
        if remaining < 10 or response.status_code == 403:
            reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            sleep_time = max(reset_time - time.time(), 0) + 1
            print(f"Rate limit hit. Sleeping {sleep_time}s...")
            time.sleep(sleep_time)
            if response.status_code == 403:
                response.raise_for_status()

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()
