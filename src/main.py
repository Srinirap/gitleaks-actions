import os
import sys
import json
import tarfile
import tempfile
import subprocess
import requests


class GitLeaksAction:
    def __init__(self):
        print("Gitleaks class...")
        self.gitleaks_version = "8.16.4"
        self.platform = os.uname().sysname.lower()
        self.arch = os.uname().machine
        self.gitleaks_bin = "gitleaks"

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

    def gitleaks_release_url(self):
        base_url = "https://github.com/zricethezav/gitleaks/releases/download"
        if self.platform == "win32":
            self.platform = "windows"

        if self.arch.startswith("x86_"):
            self.arch = self.arch.replace("x86_", "")
        return f"{base_url}/v{self.gitleaks_version}/gitleaks_{self.gitleaks_version}_{self.platform}_{self.arch}.tar.gz"

    def install_gitleaks(self):
        release_url = self.gitleaks_release_url()
        print(f"Downloading {release_url}")

        temp_dir = os.path.join(tempfile.gettempdir(), "gitleaks")
        print(f"Creating temp dir {temp_dir}")
        os.makedirs(temp_dir, exist_ok=True)

        filename = release_url.split("/")[-1]
        file_path = os.path.join(temp_dir, filename)

        with open(file_path, "wb") as infile:
            resp = requests.get(release_url)
            infile.write(resp.raw.read())

        # tar = tarfile.open(file_path)
        # tar.extractall(path=temp_dir)
        # tar.close()
        output = subprocess.check_output(f"cd {temp_dir} && tar xvf {filename}", shell=True)
        # print(output)
        print(f"Downloaded gitleaks here: {file_path}")

        self.gitleaks_bin = os.path.join(temp_dir, "gitleaks")

        output = subprocess.check_output(
            f"{self.gitleaks_bin} version", shell=True, text=True
        )
        print(f"gitleaks installed successfully with version: {output}")

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
        log_cmd = f"--log-opts=--no-merges {scan_info['base_ref']}^..{scan_info['head_ref']}"
        self.gitleaks_args.append(log_cmd)

    def gitleaks_scan(self):

        if self.event_type == "pull_request":
            # self.install_gitleaks()
            self.get_pull_request_commits()

        cmd = f"{self.gitleaks_bin} {' '.join(self.gitleaks_args)}"
        print(cmd)
        output = subprocess.check_output(cmd, shell=True)
        print(output)

    def get_push_commits(self):
        raise NotImplementedError


if __name__ == "__main__":
    GitLeaksAction().gitleaks_scan()
