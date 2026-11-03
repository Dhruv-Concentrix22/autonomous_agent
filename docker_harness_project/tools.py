"""
Tools module for Cloud MVP Harness Agent.
Provides custom restricted tools for running tests, shell commands, and creating GitHub Pull Requests.
"""

import os
import subprocess
from github import Github


def run_test_suite() -> str:
    """Executes 'pytest' inside the container workspace and returns the test output (stdout/stderr)."""
    # Assuming the cloned repo has a tests directory or conftest at root
    result = subprocess.run("pytest", shell=True, capture_output=True, text=True)
    return result.stdout or result.stderr


def run_shell_command(command: str) -> str:
    """Restricted generic command executor for git ops, etc."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return f"Error ({result.returncode}): {result.stderr}"
    return result.stdout


def create_pull_request(branch_name: str, title: str, body: str) -> str:
    """Creates a Pull Request using PyGithub."""
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPO")  # e.g., "username/repo"
    if not github_token or not repo_name:
        return "Error: GITHUB_TOKEN or GITHUB_REPO environment variable missing."

    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        # Assumes the branch has already been pushed to the remote
        pr = repo.create_pull(title=title, body=body, head=branch_name, base="main")
        return f"Successfully created PR: {pr.html_url}"
    except Exception as e:
        return f"Failed to create PR: {str(e)}"
