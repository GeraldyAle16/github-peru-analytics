import os
import time
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

def fetch_users_peru():
    users = []
    
    # We will search from 2008 to 2026, month by month to stay under the 1000 limit
    for year in range(2008, 2026):
        for month in range(1, 13):
            month_str = str(month).zfill(2)
            end_day = 30 if month in [4, 6, 9, 11] else (29 if month == 2 and year % 4 == 0 else (28 if month == 2 else 31))
            date_query = f"created:{year}-{month_str}-01..{year}-{month_str}-{end_day}"
            query = f"location:peru {date_query}"
            
            page = 1
            while True:
                url = f"https://api.github.com/search/users?q={query}&per_page=100&page={page}"
                response = requests.get(url, headers=HEADERS)
                if response.status_code == 403:
                    print('Hit limit, sleeping 60s...')
                    time.sleep(60)
                    continue
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
                time.sleep(1)
            print(f"Fetched {year}-{month_str}. Total so far: {len(users)}")
    
    df = pd.DataFrame(users).drop_duplicates(subset=['id'])
    df.to_csv('peru_users.csv', index=False)
    print(f"Saved {len(df)} users to peru_users.csv")

if __name__ == '__main__':
    fetch_users_peru()
