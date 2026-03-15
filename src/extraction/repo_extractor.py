import base64
from .github_client import GitHubClient

class RepoExtractor:
    def __init__(self, client: GitHubClient):
        self.client = client

    def get_repo_readme(self, owner: str, repo: str) -> str:
        try:
            result = self.client.make_request(f"repos/{owner}/{repo}/readme")
            if not result or "content" not in result:
                return ""
            content = base64.b64decode(result["content"]).decode("utf-8", errors='ignore')
            return content[:5000]
        except Exception:
            return ""

    def get_repo_languages(self, owner: str, repo: str) -> dict:
        result = self.client.make_request(f"repos/{owner}/{repo}/languages")
        return result if result else {}
