# serial_enroll.py (Simulated Enrollment Terminal)
import sys
import time

_simulated_local_enrollments_db = {} # UID -> {"username": ..., "unique_id": ...}

def mock_read_card():
    """Simulates reading an RFID card."""
    print("SIM_ENROLL: Waiting for card tap (simulated 3s delay)...")
    time.sleep(2)
    return f"SIM_UID_{int(time.time())}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python serial_enroll.py <username> <unique_id>", file=sys.stdout)
        sys.exit(1)

    username = sys.argv[1]
    unique_id = sys.argv[2]
    
    print(f"SIM_ENROLL: Initiating enrollment for {username} (ID: {unique_id}).")
    
    try:
        uid = mock_read_card()
        
        if uid:
            _simulated_local_enrollments_db[uid] = {"username": username, "unique_id": unique_id}
            print(f"UID_RECEIVED:{uid}", file=sys.stdout) 
            print(f"SIM_ENROLL: Card {uid} enrolled for {username}.", file=sys.stdout)
            sys.exit(0)
        else:
            print("SIM_ENROLL: Failed to read card.", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"SIM_ENROLL: An error occurred: {e}", file=sys.stderr)
        sys.exit(1)