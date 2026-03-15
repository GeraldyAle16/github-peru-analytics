import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

HEADERS = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'X-GitHub-Api-Version': '2022-11-28'
}

def fetch_sample_user_details():
    sample_username = 'torvalds'
    url = f"https://api.github.com/users/{sample_username}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        with open('user_columns_sample.json', 'w') as f:
            json.dump(data, f, indent=4)
        print("Available columns:")
        for key in data.keys():
            print(f"- {key}")

if __name__ == '__main__':
    fetch_sample_user_details()
