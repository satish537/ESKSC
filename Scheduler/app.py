from fastapi import FastAPI, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from pydantic import BaseModel, ValidationError
from datetime import datetime
import httpx

# Initialize FastAPI app
app = FastAPI()

# Initialize APScheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Define payload schema using Pydantic
class SchedulerPayload(BaseModel):
    url: str
    data: dict
    scheduled_time: datetime

# Function to execute POST requests
async def execute_post_request(url: str, data: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
        response.raise_for_status()  # Raise an error for HTTP errors
        print(f"Successfully sent POST to {url}: {response.status_code}")
    except Exception as e:
        print(f"Error sending POST to {url}: {e}")

# Endpoint to schedule a task
@app.post("/schedule-task")
async def schedule_task(payload: SchedulerPayload):
    try:
        # Validate the datetime is in the future
        if payload.scheduled_time <= datetime.now():
            raise HTTPException(status_code=400, detail="Scheduled time must be in the future.")

        # Add a job to the scheduler
        scheduler.add_job(
            execute_post_request,
            trigger=DateTrigger(run_date=payload.scheduled_time),
            args=[payload.url, payload.data],
            id=f"task-{payload.scheduled_time.timestamp()}",
            replace_existing=True
        )
        return {"message": "Task scheduled successfully", "scheduled_time": payload.scheduled_time}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Gracefully shutdown the scheduler
@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()

