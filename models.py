from pydantic import BaseModel
from datetime import datetime

class LecturerBase(BaseModel):
    id: int
    name: str
    sch_id: str
    rfid_uid: str

class StudentBase(BaseModel):
    id: int
    name: str
    sch_id: str
    rfid_uid: str

class CourseBase(BaseModel):
    code: str
    course_id: int
    title: str

class LectureSessionBase(BaseModel):
    id: int
    course_code: str
    lecturer_id: int
    session_date: datetime

class StudentAtendanceRecordBase(BaseModel):
    session_id: int
    student_id: int
    attendance_time: datetime
    attended: bool = True

class EnrollRequest(BaseModel):
    username: str
    unique_id: str

