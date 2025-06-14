# http_server.py
from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from data_store import enrollments, courses
import subprocess
import json
import time
import asyncio


app = FastAPI()

active_enrollment_websockets: dict[str, WebSocket] = {}

class EnrollRequest(BaseModel):
    username: str
    unique_id: str

class SyncRequest(BaseModel):
    course_code: str
    lecturer: str
    students: list[str]

@app.post("/cs/enroll")
async def enroll_user(data: EnrollRequest, background_tasks: BackgroundTasks):
    enrollment_session_id = f'enroll_{data.unique_id}_{int(time.time())}'
    background_tasks.add_task(_run_serial_enrollment_and_update_ws_session, data.username, data.unique_id, enrollment_session_id)
    return {
        "message": "Enrollment process initiated. Please connect to WebSocket for status updates.",
        "enrollment_session_id": enrollment_session_id,
        "websocket_url": f'ws://127.0.0.1:8000/ws/enrollment_status/{enrollment_session_id}'
        }

@app.websocket("/ws/enrollment_status/{enrollment_session_id}")
async def websocket_enrollment_status(websocket: WebSocket, enrollment_session_id: str):
    await websocket.accept()
    active_enrollment_websockets[enrollment_session_id] = websocket
    print(f"WebSocket {enrollment_session_id} connected.")
    try:
        while True:
            received_text = await websocket.receive_text()
            print(f"Received message from client on session {enrollment_session_id}, ignoring: {received_text}")
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session: {enrollment_session_id}")
    except Exception as e:
        print(f"WebSocket error for session {enrollment_session_id}: {e}")
    finally:
        await close_enrollment_ws(enrollment_session_id)

async def send_ws_message(session_id: str, message_type: str, data: dict):
    if session_id in active_enrollment_websockets:
        try:
            message = {"type": message_type, "data": data, "timestamp": time.time()}
            await active_enrollment_websockets[session_id].send_json(message)
            print(f"WS message sent to {session_id}: {message_type}")
        except Exception as e:
            print(f"Failed to send WS message to {session_id}: {e}")
            close_enrollment_ws(session_id=session_id)

async def _run_serial_enrollment_and_update_ws_session(username: str, unique_id: str, session_id: str):
    """
    Runs the serial_enroll.py script and sends updates via WebSocket.
    This function will be run in a background task.
    """

    uid = None
    await send_ws_message(session_id, "STATUS", {"stage": "INITIATED", "details": "Enrollment process started"})
    await send_ws_message(session_id, "STATUS", {"stage": "CONNECTING_ESP32", "details": "Connecting to ESP32..."})
    try:
        await send_ws_message(session_id, "STATUS", {"stage": "WAITING_FOR_CARD", "details": "Please present RFID card on terminal."})
        
        result = await asyncio.to_thread(
            subprocess.run,
            ["python3", "serial_enroll_sim.py", username, unique_id],
            capture_output=True,
            text=True,
            check=True # Raise CalledProcessError if serial_enroll.py fails
        )
        
        for line in result.stdout.splitlines():
            if line.startswith("Card ") and "enrolled for" in line:
                parts = line.split(" ")
                if len(parts) >= 2:
                    uid = parts[1]
                    break
            elif line.startswith("UID_RECEIVED:"): # If serial_enroll.py is updated to send this
                uid = line.split("UID_RECEIVED:")[1].strip()
                break

        if uid:
            enrollments[uid] = {"username": username, "unique_id": unique_id}
            await send_ws_message(session_id, "COMPLETED", {
                "message": f"Enrollment successful for {username} with UID {uid}.",
                "uid": uid,
                "username": username,
                "unique_id": unique_id,
                "success": True
            })
            print(f"Enrollment for {username} completed. UID: {uid}")
            close_enrollment_ws(session_id=session_id)
        else:
            await send_ws_message(session_id, "FAILED", {
                "message": "Enrollment failed: Could not retrieve UID from ESP32.",
                "success": False
            })
            print(f"Enrollment for {username} failed: No UID.")

    except subprocess.CalledProcessError as e:
        error_message = f"Serial enrollment script failed: {e.stderr.strip()}"
        print(error_message)
        await send_ws_message(session_id, "FAILED", {
            "message": error_message,
            "success": False,
            "details": {"stdout": e.stdout.strip(), "stderr": e.stderr.strip()}
        })
    except Exception as e:
        error_message = f"An unexpected error occurred during enrollment: {e}"
        print(error_message)
        await send_ws_message(session_id, "FAILED", {
            "message": error_message,
            "success": False
        })



async def close_enrollment_ws(session_id: str):
    """
    Closes the WebSocket connection for a given session ID and removes it
    from the active_enrollment_websockets dictionary.
    """
    if session_id in active_enrollment_websockets:
        try:
            await active_enrollment_websockets[session_id].close(code=1000)
            print(f"WebSocket for session {session_id} closed successfully.")
        except RuntimeError as e:
            print(f"Warning: Could not close WS for {session_id} due to runtime error: {e}")
        except Exception as e:
            print(f"Error closing WebSocket for session {session_id}: {e}")
        finally:
            del active_enrollment_websockets[session_id]
            print(f"Session {session_id} removed from active_enrollment_websockets.")
    else:
        print(f"WebSocket session {session_id} not found in active connections. Or already deleted.")



@app.post("/cs/sync_course")
def sync_course(data: SyncRequest):
    courses[data.course_code] = {
        "lecturer": {"name": data.lecturer, "attended": False},
        "students": [{"name": s, "attended": False} for s in data.students]
    }
    return {"message": "Course sync updated."}
