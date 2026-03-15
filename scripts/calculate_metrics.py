from datetime import datetime
from collections import Counter
import pandas as pd
import json
import os
from loguru import logger

class UserMetricsCalculator:
    def __init__(self):
        self.today = datetime.now()

    def calculate_all_metrics(self, user: dict, repos: list, classifications: list) -> dict:
        metrics = {
            "login": user["login"],
            "name": user.get("name", ""),
            "location": user.get("location", ""),
            "company": user.get("company", ""),
        }

        # Activity Metrics
        metrics["total_repos"] = len(repos)
        metrics["total_stars_received"] = sum(r.get("stargazers_count", 0) for r in repos)
        metrics["total_forks_received"] = sum(r.get("forks_count", 0) for r in repos)
        metrics["avg_stars_per_repo"] = round(metrics["total_stars_received"] / metrics["total_repos"], 2) if metrics["total_repos"] > 0 else 0

        created_at_dt = datetime.fromisoformat(user["created_at"].replace("Z", ""))
        metrics["account_age_days"] = (self.today - created_at_dt).days
        metrics["repos_per_year"] = round(metrics["total_repos"] / (metrics["account_age_days"] / 365), 2) if metrics["account_age_days"] > 0 else 0

        # Influence Metrics
        metrics["followers"] = user.get("followers", 0)
        metrics["following"] = user.get("following", 0)
        metrics["follower_ratio"] = round(metrics["followers"] / metrics["following"], 2) if metrics["following"] > 0 else metrics["followers"]
        metrics["h_index"] = self._calculate_h_index(repos)
        metrics["impact_score"] = metrics["total_stars_received"] + (metrics["total_forks_received"] * 2) + metrics["followers"]

        # Technical Metrics
        languages = [r["language"] for r in repos if r.get("language")]
        lang_counts = Counter(languages)
        top_langs = [l for l, _ in lang_counts.most_common(3)]
        metrics["primary_language_1"] = top_langs[0] if len(top_langs) > 0 else None
        metrics["primary_language_2"] = top_langs[1] if len(top_langs) > 1 else None
        metrics["primary_language_3"] = top_langs[2] if len(top_langs) > 2 else None
        metrics["language_diversity"] = len(set(languages))

        # We will map repo IDs to their GPT-4 industry if available
        repo_ids = [r["id"] for r in repos]
        user_classes = [c["industry_code"] for c in classifications if c["repo_id"] in repo_ids]
        
        metrics["industries_served"] = len(set(user_classes))
        metrics["primary_industry"] = Counter(user_classes).most_common(1)[0][0] if user_classes else None

        # Documentation quality
        repos_with_readme = sum(1 for r in repos if r.get("readme_content"))
        repos_with_license = sum(1 for r in repos if r.get("license"))
        metrics["has_readme_pct"] = round(repos_with_readme / len(repos), 2) if repos else 0
        metrics["has_license_pct"] = round(repos_with_license / len(repos), 2) if repos else 0

        # Engagement Metrics
        metrics["total_open_issues"] = sum(r.get("open_issues_count", 0) for r in repos)

        if repos:
            pushed_dates = []
            for r in repos:
                if r.get("pushed_at"):
                    pushed_dates.append(datetime.fromisoformat(r["pushed_at"].replace("Z", "")))
            
            if pushed_dates:
                last_push = max(pushed_dates)
                metrics["days_since_last_push"] = (self.today - last_push).days
                metrics["is_active"] = metrics["days_since_last_push"] < 90
            else:
                metrics["days_since_last_push"] = None
                metrics["is_active"] = False
        else:
            metrics["days_since_last_push"] = None
            metrics["is_active"] = False

        return metrics

    def _calculate_h_index(self, repos: list) -> int:
        stars = sorted([r.get("stargazers_count", 0) for r in repos], reverse=True)
        h = 0
        for i, s in enumerate(stars):
            if s >= i + 1:
                h = i + 1
            else:
                break
        return h

def main():
    if not os.path.exists("data/raw/users/users_detailed.json"):
        logger.error("No user data found. Run extract_data.py first.")
        return
        
    logger.info("Loading detailed users, repos, and classifications...")
    with open("data/raw/users/users_detailed.json", "r", encoding="utf-8") as f:
        users = json.load(f)
    with open("data/raw/repos/repos_detailed.json", "r", encoding="utf-8") as f:
        repos = json.load(f)
        
    classifications = []
    if os.path.exists("data/processed/classifications.csv"):
        classifications = pd.read_csv("data/processed/classifications.csv").to_dict('records')

    calc = UserMetricsCalculator()
    user_metrics_list = []
    
    logger.info("Computing metrics per user...")
    for u in users:
        u_repos = [r for r in repos if r['owner']['login'] == u['login']]
        m = calc.calculate_all_metrics(u, u_repos, classifications)
        user_metrics_list.append(m)
        
    # Save User Metrics
    os.makedirs("data/metrics", exist_ok=True)
    df_users = pd.DataFrame(user_metrics_list)
    df_users.to_csv("data/processed/users.csv", index=False)
    
    # Save a flat repositories.csv for the dashboard's repo browser
    flat_repos = []
    for r in repos:
        c_code = next((c['industry_name'] for c in classifications if c['repo_id'] == r['id']), "Unknown")
        flat_repos.append({
            "id": r["id"],
            "name": r["name"],
            "owner": r["owner"]["login"],
            "description": r.get("description", ""),
            "language": r.get("language", ""),
            "stargazers_count": r.get("stargazers_count", 0),
            "forks_count": r.get("forks_count", 0),
            "open_issues_count": r.get("open_issues_count", 0),
            "created_at": r.get("created_at", ""),
            "updated_at": r.get("updated_at", ""),
            "industry": c_code
        })
    df_repos = pd.DataFrame(flat_repos)
    df_repos.to_csv("data/processed/repositories.csv", index=False)
    
    # Calculate global ecosystem metrics
    eco_metrics = {
        "total_developers": len(df_users),
        "total_repositories": len(df_repos),
        "total_stars": int(df_repos["stargazers_count"].sum()),
        "avg_repos_per_user": float(round(df_users["total_repos"].mean(), 2)),
        "active_developer_pct": float(round((df_users["is_active"].sum() / len(df_users)) * 100, 2)),
        "avg_account_age_days": float(round(df_users["account_age_days"].mean(), 2)),
        "most_popular_languages": df_users["primary_language_1"].value_counts().head(10).to_dict(),
        "industry_distribution": df_repos["industry"].value_counts().to_dict()
    }
    
    with open("data/metrics/ecosystem_metrics.json", "w", encoding="utf-8") as f:
        json.dump(eco_metrics, f, indent=4)
        
    logger.info("Metrics calculation complete! Saved users.csv, repositories.csv, and ecosystem_metrics.json")

if __name__ == "__main__":
    main()
