import os
import sys
import json
import subprocess
import requests


class GitLeaksAction:
    def __init__(self):
        print("Gitleaks class...")
        self.base_url = os.environ["GITHUB_API_URL"]
        self.gh_token = os.environ["GITHUB_TOKEN"]
        self.event_type = os.environ["GITHUB_EVENT_NAME"]
        self.owner, self.repo = os.environ["GITHUB_REPOSITORY"].rsplit("/")
        event_json_path = os.environ["GITHUB_EVENT_PATH"]

        with open(event_json_path, "r") as f:
            self.gh_events = json.loads(f.read())

        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.gh_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        self.gitleaks_args = [
            "detect",
            "--redact",
            "-v",
            "--exit-code=2",
            "--report-format=sarif",
            "--report-path=results.sarif",
            "--log-level=debug",
        ]

    def get_commits(self):
        if self.event_type == "pull_request":
            self.get_pull_request_commits()
        elif self.event_type == "push":
            self.get_push_commits()

    def get_pull_request_commits(self):
        print("Getting pull request commits...")
        pr_number = self.gh_events["number"]
        pr_url = (
            f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls/{pr_number}/commits"
        )
        response = requests.get(pr_url, headers=self.headers)

        commits = response.json()

        scan_info = {
            "base_ref": commits[0]["sha"],
            "head_ref": commits[len(commits) - 1]["sha"],
        }
        log_cmd = f"--log-opts=--no-merges --first-parent {scan_info['base_ref']}^..{scan_info['head_ref']}"
        self.gitleaks_args.append(log_cmd)

    def gitleaks_scan(self):

        if self.event_type == "pull_request":
            self.get_pull_request_commits()

        cmd = f"gitleaks {' '.join(self.gitleaks_args)}"
        print(cmd)
        subprocess.run(cmd, shell=True)

    def get_push_commits(self):
        raise NotImplementedError


if __name__ == "__main__":
    GitLeaksAction().gitleaks_scan()
