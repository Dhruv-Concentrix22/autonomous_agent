"""
AI Harness Learning Project: True Containerized Bug Hunt Framework
===================================================================

This harness runs 100% INSIDE the Docker container.
The agent, code edits, command execution, and tests are completely jailed inside /app.
Uses Restricted Custom Tools (Least Privilege Model).
"""

import asyncio
import os
import subprocess
import sys
import time
from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig
from google.antigravity.hooks.policy import allow_all

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def run_test_suite() -> str:
    """Executes 'pytest' inside the container workspace and returns the test output (stdout/stderr)."""
    result = subprocess.run("pytest", shell=True, capture_output=True, text=True)
    return result.stdout or result.stderr

async def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY environment variable is missing inside the container!")
        print("Make sure to pass it when starting the container:")
        print("  docker run --rm --env-file .env bug-hunt-harness\n")
        sys.exit(1)

    # Sanitize API key (strip quotes or trailing whitespace if present in .env)
    api_key = api_key.strip().strip('"\'')
    masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"

    print("="*60)
    print("RUNNING HARNESS INSIDE ISOLATED DOCKER CONTAINER (/app)")
    print(f"API Key Detected: {masked_key} (Length: {len(api_key)})")
    print("Security Model: Restricted Custom Tooling (No Generic Shell)")
    print("="*60)

    # 1. Initial Evaluation (Verify failing baseline)
    print("\n[Phase 1: Initial Baseline Evaluation]")
    output = run_test_suite()
    print("Initial Pytest Output:")
    print(output)
    
    # 2. Agent Execution Phase (Jailed inside container with restricted tool)
    print("="*60)
    print("[Phase 2: Agent Orchestration & Execution]")
    print("="*60)
    
    system_instruction = (
        "You are an expert AI debugging agent operating inside a Linux container sandbox (/app).\n"
        "Your workspace contains:\n"
        "  - 'buggy_code.py': contains a math bug in calculate_totals().\n"
        "  - 'test_buggy_code.py': unit tests.\n\n"
        "Instructions:\n"
        "1. Read 'buggy_code.py' and 'test_buggy_code.py' in /app.\n"
        "2. Identify why calculate_totals() fails.\n"
        "3. Edit 'buggy_code.py' to fix the math bug so that discount_percent is properly applied as a percentage.\n"
        "4. Call the restricted tool `run_test_suite()` to verify your fix."
    )
    
    config = LocalAgentConfig(
        api_key=api_key,
        system_instructions=system_instruction,
        capabilities=CapabilitiesConfig(disabled_tools=['run_command']), # Disable generic shell execution!
        tools=[run_test_suite],                                           # Expose ONLY the hyper-specific test tool!
        policies=[allow_all()]
    )
    
    print("Initializing Antigravity Agent with Restricted Tools...")
    start_time = time.time()
    
    async with Agent(config) as agent:
        prompt = (
            "Please inspect /app/buggy_code.py and /app/test_buggy_code.py, "
            "fix the bug in calculate_totals(), and use the tool `run_test_suite()` to verify that pytest passes."
        )
        print(f"Sending prompt to Agent: '{prompt}'\n")
        
        response = await agent.chat(prompt)
        
        async for token in response:
            sys.stdout.write(token)
            sys.stdout.flush()
        print()
        
    elapsed = time.time() - start_time
    print(f"\nAgent execution completed in {elapsed:.2f} seconds.")

    # 3. Final Deterministic Evaluation Phase
    print("\n" + "="*60)
    print("[Phase 3: Final Deterministic Evaluation]")
    print("="*60)
    
    final_output = run_test_suite()
    print("\n--- Final Pytest Output ---")
    print(final_output)
    print("---------------------------")
    
    if "4 passed" in final_output:
        print("RESULT: ✅ PASS - The agent fixed the bug inside the sandbox container!")
    else:
        print("RESULT: ❌ FAIL - Tests are still failing inside the container.")

if __name__ == "__main__":
    asyncio.run(main())
