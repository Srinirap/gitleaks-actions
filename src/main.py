import os
import sys
import json


def parse_json(json_string):
    print("Printing json content")
    print(json.dumps(json_string))


def get_commits(event_name="pull_request"):
    base_url = os.environ["GITHUB_API_URL"]
    gh_token = os.environ["GITHUB_TOKEN"]
    event_type = os.environ["GITHUB_EVENT_NAME"]
    owner, repo = os.environ["GITHUB_REPOSITORY"].rsplit("/")

    print(base_url, gh_token, event_type, owner, repo)


if __name__ == "__main__":
    print(sys.argv)
    get_commits()
