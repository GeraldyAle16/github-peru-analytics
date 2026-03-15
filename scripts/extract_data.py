import os
import sys
import pandas as pd
from loguru import logger
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extraction.github_client import GitHubClient
from src.extraction.user_extractor import UserExtractor
from src.extraction.repo_extractor import RepoExtractor

def main():
    client = GitHubClient()
    user_ext = UserExtractor(client)
    repo_ext = RepoExtractor(client)
    
    # Load users to process
    search_csv = "peru_users.csv"
    if not os.path.exists(search_csv):
        logger.error(f"Cannot find {search_csv}. Please run initial search first.")
        return
        
    df = pd.read_csv(search_csv)
    # The instructions specifically mandate exactly 1,000 top GitHub users.
    # We will pick the first 1,000 users from the CSV.
    logins = df['login'].head(1000).tolist()
    
    users_data = []
    repos_data = []
    
    logger.info(f"Starting extraction for EXACTLY {len(logins)} users...")
    
    for idx, login in enumerate(logins, 1):
        if idx % 10 == 0:
            logger.info(f"Processing user {idx}/{len(logins)}: {login}")
            
        try:
            # 1. Get detailed User Data (Name, location, followers, created_at, etc.)
            user_details = user_ext.get_user_details(login)
            if not user_details:
                continue
            users_data.append(user_details)
            
            # 2. Get User Repos (forks excluded as per instructions: "only owned repos, not forks")
            user_repos = user_ext.get_user_repos(login)
            for r in user_repos:
                if not r['fork']:
                    repos_data.append(r)
                    
        except Exception as e:
            logger.error(f"Error processing {login}: {str(e)}")
            
    # Save raw data for Users and Repos immediately
    logger.info("Saving raw data arrays...")
    os.makedirs("data/raw/users", exist_ok=True)
    os.makedirs("data/raw/repos", exist_ok=True)
    
    with open("data/raw/users/users_detailed.json", "w", encoding="utf-8") as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)
        
    with open("data/raw/repos/repos_detailed.json", "w", encoding="utf-8") as f:
        json.dump(repos_data, f, ensure_ascii=False, indent=2)
        
    # The assignment says "Each student must collect data on at least 1,000 repositories from Peru."
    # We will sort the extracted repos by stargazers_count descending and grab the top 1000 repositories across all users.
    logger.info("Extracting README and Languages for Top 1000 Repositories by Stars...")
    repos_data.sort(key=lambda x: x.get('stargazers_count', 0), reverse=True)
    top_1000_repos = repos_data[:1000]
    
    top_repos_enriched = []
    for idx, repo in enumerate(top_1000_repos, 1):
        if idx % 50 == 0:
            logger.info(f"Enriching repo {idx}/1000: {repo['full_name']}")
        try:
            # 3. Get README and Languages for the Repo (needed for AI classification later)
            readme = repo_ext.get_repo_readme(repo['owner']['login'], repo['name'])
            languages = repo_ext.get_repo_languages(repo['owner']['login'], repo['name'])
            
            repo_copy = repo.copy()
            repo_copy['readme_content'] = readme
            repo_copy['languages_dict'] = languages
            top_repos_enriched.append(repo_copy)
        except Exception as e:
            logger.error(f"Error enriching {repo['full_name']}: {str(e)}")
            
    with open("data/raw/repos/top_repos_enriched.json", "w", encoding="utf-8") as f:
        json.dump(top_repos_enriched, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Completed! Extracted {len(users_data)} detailed users and enriched the top {len(top_repos_enriched)} repos.")

if __name__ == "__main__":
    main()
