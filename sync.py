import sqlite3
from typing import Optional, List
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Response
from models import LecturerBase, StudentBase, CourseBase
from database import get_db_connection


class Sync:
    def __init__(self, app: FastAPI):
        self.app = app
        self._register_routes()
    
    def _register_routes(self):
        @self.app.post("/cs/sync/lecturers")
        async def sync_lecturers(lecturer: LecturerBase, db: sqlite3.Connection = Depends(get_db_connection)):
            cursor = db.cursor()
            try:
                if lecturer is not None:
                    cursor.execute("""
                        INSERT INTO lecturers (id, name, sch_id, rfid_uid) VALUES (?, ?, ?, ?);""", 
                        (lecturer.id, lecturer.name, lecturer.sch_id, lecturer.rfid_uid))
                else:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid lecturer data provided")
                db.commit()
                print(f"Successfully synced lecturer: {lecturer.name} with ID {lecturer.sch_id}")
                return Response(status_code=status.HTTP_201_CREATED)
            except sqlite3.IntegrityError as e:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, details=f"Integrity error syncing lecturer: {e}")
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details=f"Error syncing lecturer: {e}")
            finally:
                cursor.close()
                
        @self.app.post("/cs/sync/students")
        async def sync_students(student: StudentBase, db: sqlite3.Connection = Depends(get_db_connection)):
            print(f"Received lecturer sync request: {student}")
            cursor = db.cursor()
            try:
                if student is not None:
                    cursor.execute("""
                        INSERT INTO students (id, name, sch_id, rfid_uid) VALUES (?, ?, ?, ?);"""
                        (student.id, student.name, student.sch_id, student.rfid_uid))
                else:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid student data provided")
                db.commit()
                print(f"Successfully synced student: {student.name} with ID {student.sch_id}")
                return Response(status_code=status.HTTP_201_CREATED)
            except sqlite3.IntegrityError as e:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, details=f"Integrity error syncing lecturer: {e}")
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details=f"Error syncing lecturer: {e}")

        @self.app.post("/cs/sync/courses")
        async def sync_courses(course: CourseBase, db: sqlite3.Connection = Depends(get_db_connection)):
        
            try:
                cursor = db.cursor()
                if course is not None:
                    cursor.execute("""
                        INSERT INTO courses (code, course_id, title) VALUES (?, ?, ?)""", 
                        (course.code, course.course_id, course.title))
                    db.commit()
                    print(f"Successfully synced course: {course.title} with code {course.code}")
                else:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid course data provided")
                db.commit()
                print(f"Successfully synced course: {course.title} with code {course.code}")
                
            except sqlite3.IntegrityError as e:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, details=f"Integrity error syncing course: {e}")
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details=f"Error syncing course: {e}")
                
        @self.app.get("/cs/sync/lecturers", response_model=List[LecturerBase])
        async def get_lecturers(db: sqlite3.Connection = Depends(get_db_connection)):
            cursor = db.cursor()
            cursor.execute("SELECT id, name, sch_id, rfid_uid FROM lecturers;")
            rows = cursor.fetchall()
            list_of_dicts = [dict(row) for row in rows]
            print(rows, list_of_dicts)
            if not rows:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No lecturers found")
            return list_of_dicts

        @self.app.delete("/cs/sync/lecturers",)
        async def delete_lecturers(db: sqlite3.Connection = Depends(get_db_connection)):
            cursor = db.cursor()
            try:
                cursor.execute("DELETE FROM lecturers;")
                db.commit()
                print("All lecturers deleted successfully.")
                return {"message": "All lecturers deleted successfully."}
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting lecturers: {e}")
            finally:
                cursor.close()