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
    result = subprocess.run(["pytest"], capture_output=True, text=True)
    return result.stdout or result.stderr

def create_git_branch(branch_name: str) -> str:
    """Create and switch to a brand new git branch."""
    branch_res = subprocess.run(
        ["git", "checkout", "-b", branch_name], 
        capture_output=True,  
        text=True,            
        check=False 
    )
    if branch_res.returncode != 0:
        return f"Error creating branch '{branch_name}': {branch_res.stderr.strip()}"
    return f"Successfully created and switched to branch '{branch_name}'."

def git_commit(message: str) -> str:
    """Stages all changes and creates a commit."""
    add_res = subprocess.run(
        ["git", "add", "."], 
        capture_output=True,  
        text=True,            
        check=False 
    )
    if add_res.returncode != 0:
        return f"Error staging changes: {add_res.stderr.strip()}"
    commit_res = subprocess.run(
        ["git", "commit", "-m", message], 
        capture_output=True,  
        text=True,            
        check=False 
    )
    if commit_res.returncode != 0:
        error_msg = commit_res.stderr.strip() or commit_res.stdout.strip()
        return f"Error committing changes: {error_msg}"
    return f"Successfully committed changes with message: '{message}'."

def push_branch(branch_name: str) -> str:
    """Pushes the local branch to the remote origin."""
    push_res = subprocess.run(
        ["git", "push", "--set-upstream", "origin", branch_name], 
        capture_output=True,  
        text=True,            
        check=False 
    )
    if push_res.returncode != 0:
        return f"Error pushing branch '{branch_name}': {push_res.stderr.strip()}"
    return f"Successfully pushed branch '{branch_name}' to remote origin."

def get_git_status() -> str:
    """Returns the working directory status."""
    status_res = subprocess.run(
        ["git", "status", "-s"], 
        capture_output=True,  
        text=True,            
        check=False 
    )
    return status_res.stdout.strip() or "Clean working tree (no changes)."

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
