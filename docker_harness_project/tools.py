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

def list_files(directory: str = ".") -> str:
    """Lists files in the workspace directory, excluding git and cache folders."""
    try:
        file_list = []
        ignore_dirs = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", ".egg-info"}
        
        for root, dirs, files in os.walk(directory):
            # Exclude ignored directories in-place
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), directory)
                file_list.append(rel_path)
                
        if not file_list:
            return f"No files found in directory '{directory}'."
            
        return "\n".join(sorted(file_list))
    except Exception as e:
        return f"Error listing files in '{directory}': {str(e)}"

def read_file(file_path: str) -> str:
    """Reads and returns the content of a file."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist."
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"

def write_file(file_path: str, content: str) -> str:
    """Overwrites or creates a file with the given content."""
    try:
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully written content to '{file_path}'."
    except Exception as e:
        return f"Error writing file '{file_path}': {str(e)}"



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
