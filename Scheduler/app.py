from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from datetime import datetime
import uuid
import json
import os

app = FastAPI()
scheduler = BackgroundScheduler()
scheduler.start()

JOBS_FILE = "jobs.json"

# Ensure jobs file exists
if not os.path.exists(JOBS_FILE):
    with open(JOBS_FILE, "w") as f:
        json.dump([], f)

class JobRequest(BaseModel):
    url: str
    payload: dict
    run_at: datetime  # Format: "YYYY-MM-DD HH:MM:SS"

# Load jobs from JSON file
def load_jobs():
    with open(JOBS_FILE, "r") as f:
        return json.load(f)

# Save jobs to JSON file
def save_jobs(jobs):
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=4, default=str)

# Function to execute the job
def execute_job(job_id, url, payload):
    try:
        response = requests.post(url, json=payload)
        print(f"POST request sent to {url} with status {response.status_code}")
    except Exception as e:
        print(f"Failed to send request: {str(e)}")

    # Remove job from JSON file after execution
    jobs = load_jobs()
    jobs = [job for job in jobs if job["id"] != job_id]
    save_jobs(jobs)

# Endpoint to schedule a job
@app.post("/schedule-job/")
def schedule_job(job_request: JobRequest):
    job_id = str(uuid.uuid4())  # Generate unique job ID
    job_data = {
        "id": job_id,
        "url": job_request.url,
        "payload": job_request.payload,
        "run_at": job_request.run_at,
    }

    # Save job to JSON file
    jobs = load_jobs()
    jobs.append(job_data)
    save_jobs(jobs)

    # Schedule the job in APScheduler
    scheduler.add_job(
        execute_job,
        "date",
        run_date=job_request.run_at,
        args=[job_id, job_request.url, job_request.payload],
        id=job_id,
    )

    return {"message": "Job scheduled", "job_id": job_id}

# Endpoint to get all scheduled jobs from JSON
@app.get("/jobs/")
def get_jobs():
    return load_jobs()

# Endpoint to remove a job
@app.delete("/jobs/{job_id}")
def remove_job(job_id: str):
    jobs = load_jobs()
    new_jobs = [job for job in jobs if job["id"] != job_id]
    
    if len(jobs) == len(new_jobs):
        raise HTTPException(status_code=404, detail="Job not found")

    save_jobs(new_jobs)
    scheduler.remove_job(job_id)

    return {"message": "Job removed", "job_id": job_id}
