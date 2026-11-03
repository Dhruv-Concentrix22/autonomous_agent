"""
Cloud MVP Harness: Autonomous Issue Solver
===================================================================

This harness runs inside a Google Cloud Run Job.
It receives GitHub details dynamically, clones the repo, fixes the issue,
and submits a Pull Request back to GitHub.
"""

import asyncio
import os
import subprocess
import sys
import time
from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
from google.antigravity.hooks.policy import allow_all

from tools import run_test_suite, run_shell_command, create_pull_request

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

async def main():
    api_key = os.getenv("GEMINI_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    repo_url = os.getenv("GITHUB_REPO_URL") # Full URL for cloning
    repo_name = os.getenv("GITHUB_REPO")    # user/repo format for PyGithub
    issue_number = os.getenv("ISSUE_NUMBER")
    issue_description = os.getenv("ISSUE_DESCRIPTION")
    
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY is missing!")
        sys.exit(1)
    if not github_token or not repo_url or not issue_number:
         print("❌ ERROR: Missing GitHub specific environment variables!")
         sys.exit(1)

    api_key = api_key.strip().strip('"\'')

    print("="*60)
    print("RUNNING CLOUD MVP HARNESS INSIDE DOCKER CONTAINER")
    print(f"Target Repository: {repo_url}")
    print(f"Target Issue: #{issue_number}")
    print("="*60)

    # 1. Clone the repository dynamically
    print("\n[Phase 1: Environment Initialization]")
    # We embed the token in the URL for pushing later
    auth_repo_url = repo_url.replace("https://", f"https://oauth2:{github_token}@")
    clone_cmd = f"git clone {auth_repo_url} /app/repo"
    print("Cloning repository...")
    subprocess.run(clone_cmd, shell=True, check=True)
    
    # Change working directory to the cloned repo
    os.chdir("/app/repo")
    print(f"Working directory changed to: {os.getcwd()}")
    
    # Configure git identity for commits
    subprocess.run("git config --global user.email 'ai-agent@example.com'", shell=True)
    subprocess.run("git config --global user.name 'Antigravity AI Agent'", shell=True)
    
    # 2. Agent Execution Phase
    print("\n" + "="*60)
    print("[Phase 2: Agent Orchestration & Execution]")
    print("="*60)
    
    system_instruction = (
        "You are an expert autonomous software engineer agent operating inside a secure Linux container sandbox.\n"
        f"You have just cloned the repository into '{os.getcwd()}'.\n\n"
        "Your goal is to fix the following GitHub issue:\n"
        f"ISSUE TITLE/DESCRIPTION:\n{issue_description}\n\n"
        "Instructions:\n"
        "1. Read the codebase to understand the bug described in the issue.\n"
        "2. Create a new git branch (e.g., `git checkout -b fix/issue-XYZ`).\n"
        "3. Edit the necessary files to fix the bug.\n"
        "4. Run tests to verify your fix using `run_test_suite()`.\n"
        "5. If tests pass, commit your changes (`git commit -am 'Fix bug'`).\n"
        "6. Push the branch to the remote (`git push origin <branch_name>`).\n"
        f"7. Call the `create_pull_request` tool to open a PR closing Issue #{issue_number}.\n"
        "NOTE: To run shell/git commands (like branch, commit, push), use the `run_shell_command` tool."
    )
    
    config = LocalAgentConfig(
        api_key=api_key,
        system_instructions=system_instruction,
        capabilities=CapabilitiesConfig(disabled_tools=['run_command']), 
        tools=[run_test_suite, run_shell_command, create_pull_request],
        policies=[allow_all()]
    )
    
    print("Initializing Antigravity Agent...")
    start_time = time.time()
    
    async with Agent(config) as agent:
        prompt = (
            f"Please fix GitHub Issue #{issue_number}. Read the code, apply the fix, verify with tests, "
            "commit your changes to a new branch, push it, and create a Pull Request."
        )
        print(f"Sending prompt to Agent...\n")
        
        response = await agent.chat(prompt)
        
        async for token in response:
            sys.stdout.write(token)
            sys.stdout.flush()
        print()
        
    elapsed = time.time() - start_time
    print(f"\nAgent execution completed in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    asyncio.run(main())