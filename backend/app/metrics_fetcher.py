import requests
import yaml

def fetch_metrics():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    org = config['github']['org']
    token = config['github']['token']
    url = f'https://api.github.com/orgs/{org}/copilot/metrics'
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch metrics: {response.status_code}")
        return []