import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

HEADERS = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'X-GitHub-Api-Version': '2022-11-28'
}

def verify_fetch_users():
    users = []
    # Test just for Jan 2024
    year = 2024
    month_str = "01"
    end_day = 31
    date_query = f"created:{year}-{month_str}-01..{year}-{month_str}-{end_day}"
    query = f"location:peru {date_query}"
    
    page = 1
    while True:
        url = f"https://api.github.com/search/users?q={query}&per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            break
        
        data = response.json()
        items = data.get('items', [])
        if not items:
            break
        
        for item in items:
            users.append({'login': item['login'], 'id': item['id'], 'html_url': item['html_url'], 'type': item['type']})
        
        if len(items) < 100:
            break
        page += 1
        
    df = pd.DataFrame(users).drop_duplicates(subset=['id'])
    df.to_csv('peru_users_verification.csv', index=False)
    print(f"Verified successfully. Downloaded {len(df)} users for Jan 2024 to peru_users_verification.csv")

if __name__ == '__main__':
    verify_fetch_users()
