from .github_client import GitHubClient

class UserExtractor:
    def __init__(self, client: GitHubClient):
        self.client = client

    def get_user_details(self, username: str) -> dict:
        return self.client.make_request(f"users/{username}")

    def get_user_repos(self, username: str) -> list[dict]:
        repos = []
        page = 1
        while True:
            result = self.client.make_request(
                f"users/{username}/repos",
                params={"per_page": 100, "page": page, "type": "owner", "sort": "updated", "direction": "desc"}
            )
            if not result:
                break
            repos.extend(result)
            if len(result) < 100:
                break
            page += 1
        return repos
