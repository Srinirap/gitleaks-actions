import os
import sys
import json

import requests



def get_commits(event_name="pull_request"):
    print("Getting commits...")
    base_url = os.environ["GITHUB_API_URL"]
    gh_token = os.environ["GITHUB_TOKEN"]
    event_type = os.environ["GITHUB_EVENT_NAME"]
    owner, repo = os.environ["GITHUB_REPOSITORY"].rsplit("/")
    event_json_path = os.environ["GITHUB_EVENT_PATH"]

    print(base_url, gh_token, event_type, owner, repo, event_json_path)

    json_data = json.load(open(event_json_path))
    print(json_data)
    pull_request_number = json_data["number"]

    pr_url = f"{base_url}/repos/{owner}/{repo}/pulls/{pull_request_number}/commits"

    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {gh_token}", "X-GitHub-Api-Version": "2022-11-28"}
    print(pr_url)

    response = requests.get(url=pr_url, headers=headers)

    print(response)
    print("""Boooooooooooo""")
    print(response.json())





if __name__ == "__main__":
    print(sys.argv)
    get_commits()
