"""
Cloud MVP: GitHub Webhook Receiver (Cloud Run Service)
======================================================

Receives GitHub Webhook events for opened issues, immediately responds 200 OK,
and asynchronously triggers the Cloud Run Job (Agent Harness Container).
"""

import os
import asyncio
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Header
from google.cloud import run_v2
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="GitHub Webhook Receiver for AI Harness",
    description="Listens for GitHub issue events and triggers Cloud Run Agent Jobs",
    version="1.0.0"
)

# Configuration from Environment Variables
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-gcp-project-id")
GCP_REGION = os.getenv("GCP_REGION", "us-central1")
CLOUD_RUN_JOB_NAME = os.getenv("CLOUD_RUN_JOB_NAME", "bug-hunt-agent-job")


def trigger_cloud_run_job(repo_url: str, repo_name: str, issue_number: int, issue_title: str, issue_body: str):
    """
    Triggers the Google Cloud Run Job with custom environment variables for the issue context.
    Runs asynchronously in the background after 200 OK is returned to GitHub.
    """
    print(f"🚀 Triggering Cloud Run Job '{CLOUD_RUN_JOB_NAME}' for issue #{issue_number} in {repo_name}...")
    
    # Combined issue prompt context
    full_issue_description = f"Title: {issue_title}\n\nDescription:\n{issue_body}"

    # If running locally or without GCP credentials, log mock trigger
    if os.getenv("MOCK_CLOUD_RUN", "true").lower() == "true":
        print("ℹ️ [MOCK] Cloud Run Job trigger simulated successfully!")
        print(f"   REPO_URL: {repo_url}")
        print(f"   REPO: {repo_name}")
        print(f"   ISSUE: #{issue_number}")
        print(f"   DESCRIPTION:\n{full_issue_description}")
        return

    try:
        client = run_v2.JobsClient()
        job_path = f"projects/{GCP_PROJECT_ID}/locations/{GCP_REGION}/jobs/{CLOUD_RUN_JOB_NAME}"
        
        # Override container environment variables dynamically for this execution
        request = run_v2.RunJobRequest(
            name=job_path,
            overrides=run_v2.RunJobRequest.Overrides(
                container_overrides=[
                    run_v2.RunJobRequest.Overrides.ContainerOverride(
                        env=[
                            run_v2.EnvVar(name="GITHUB_REPO_URL", value=repo_url),
                            run_v2.EnvVar(name="GITHUB_REPO", value=repo_name),
                            run_v2.EnvVar(name="ISSUE_NUMBER", value=str(issue_number)),
                            run_v2.EnvVar(name="ISSUE_DESCRIPTION", value=full_issue_description),
                        ]
                    )
                ]
            )
        )
        
        operation = client.run_job(request=request)
        print(f"✅ Cloud Run Job execution initiated: {operation.operation.name}")
    except Exception as e:
        print(f"❌ Failed to trigger Cloud Run Job: {str(e)}")


@app.get("/")
def health_check():
    """Health check endpoint for Cloud Run."""
    return {"status": "healthy", "service": "webhook-receiver"}


@app.post("/webhook")
async def handle_github_webhook(
    request: Request,
    x_github_event: str = Header(None)
):
    """
    Primary Webhook Endpoint.
    Parses GitHub payload and dispatches background Cloud Run Job.
    """
    payload = await request.json()
    
    # Handle GitHub Ping Event (sent when webhook is first configured)
    if x_github_event == "ping":
        return {"status": "pong", "message": "Webhook successfully connected!"}

    # Process only 'issues' events when an issue is opened
    action = payload.get("action")
    if x_github_event == "issues" and action in ["opened", "reopened"]:
        issue = payload.get("issue", {})
        repo = payload.get("repository", {})
        
        repo_url = repo.get("clone_url")
        repo_name = repo.get("full_name")  # format: 'owner/repo'
        issue_number = issue.get("number")
        issue_title = issue.get("title", "")
        issue_body = issue.get("body", "")

        print(f"📩 Received 'issues.{action}' webhook for {repo_name} Issue #{issue_number}")

        # Dispatch execution in background task so HTTP response returns instantly (< 1 sec)
        return FastAPI_response_with_background_task(
            repo_url, repo_name, issue_number, issue_title, issue_body
        )

    return {"status": "ignored", "message": f"Event '{x_github_event}.{action}' is ignored."}


def FastAPI_response_with_background_task(repo_url, repo_name, issue_number, issue_title, issue_body):
    from fastapi.responses import JSONResponse
    
    # Trigger background task
    asyncio.create_task(
        asyncio.to_thread(
            trigger_cloud_run_job, repo_url, repo_name, issue_number, issue_title, issue_body
        )
    )
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "accepted",
            "message": f"Agent job dispatched for Issue #{issue_number}",
            "repository": repo_name
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
