# serial_enroll.py
import sys
import time
from data_store import enrollments

def mock_read_card():
    time.sleep(3)  # Simulate card tap
    return "UID12345"

if __name__ == "__main__":
    username = sys.argv[1]
    unique_id = sys.argv[2]
    print(f"Waiting for card scan for {username}...")
    uid = mock_read_card()
    enrollments[uid] = {"username": username, "unique_id": unique_id}
    print(f"Card {uid} enrolled for {username}.")

