# http_server.py
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from data_store import enrollments, courses
import subprocess
import json

app = FastAPI()

class EnrollRequest(BaseModel):
    username: str
    unique_id: str

class SyncRequest(BaseModel):
    course_code: str
    lecturer: str
    students: list[str]

@app.post("/cs/enroll")
def enroll_user(data: EnrollRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_serial_enrollment, data.username, data.unique_id)
    return {"message": "Enrollment started."}

def run_serial_enrollment(username, unique_id):
    result = subprocess.run(["python3", "serial_enroll.py", username, unique_id], capture_output=True)
    print(result.stdout.decode())

@app.post("/cs/sync_course")
def sync_course(data: SyncRequest):
    courses[data.course_code] = {
        "lecturer": {"name": data.lecturer, "attended": False},
        "students": [{"name": s, "attended": False} for s in data.students]
    }
    return {"message": "Course sync updated."}
