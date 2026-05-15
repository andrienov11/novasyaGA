from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from scheduler_core import run_scheduler

app = FastAPI(title="Novasya Scheduler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs = {}


class ScheduleRequest(BaseModel):
    data: list
    rooms: list
    days: list
    sessions: list
    lecturer_per_class: int
    pop_size: int = 500
    gens: int = 300
    mut_rate: float = 0.2
    sks_per_session: int = 2


def process_job(job_id: str, req: ScheduleRequest):
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10

        result = run_scheduler(
            data=req.data,
            rooms=req.rooms,
            days=req.days,
            sessions=req.sessions,
            lecturer_per_class=req.lecturer_per_class,
            pop_size=req.pop_size,
            gens=req.gens,
            mut_rate=req.mut_rate,
            sks_per_session=req.sks_per_session
        )

        jobs[job_id]["status"] = "done"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["result"] = result

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)


@app.get("/")
def root():
    return {"message": "Novasya Scheduler API is running"}


@app.post("/generate")
def generate(req: ScheduleRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "status": "queued",
        "progress": 0,
        "result": None,
        "error": None
    }

    background_tasks.add_task(process_job, job_id, req)

    return {"job_id": job_id}


@app.get("/status/{job_id}")
def status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})