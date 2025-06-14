# serial_enroll.py
import serial
import sys
import time

BAUD_RATE = 115200
SERIAL_TIMEOUT = 30  # Total time to wait for scan (command + UID)

def communicate_with_esp32(user_id: str, user_name: str, serial_port: str):
    try:
        print(f"[HOST] Connecting to {serial_port}...")
        ser = serial.Serial(serial_port, BAUD_RATE, timeout=1)
        time.sleep(2)

        ser.reset_input_buffer()
        ser.reset_output_buffer()

        command = f"ENROLL:{user_id}:{user_name}\n"
        print(f"[HOST] Sending: {command.strip()}")
        ser.write(command.encode())

        start_time = time.time()
        buffer = ""

        while time.time() - start_time < SERIAL_TIMEOUT:
            if ser.in_waiting:
                char = ser.read().decode()
                buffer += char
                if "\n" in buffer:
                    line = buffer.strip()
                    print(f"[HOST] Got: {line}")
                    if line.startswith("UID:"):
                        uid = line.split("UID:")[1]
                        print(f"UID_RECEIVED:{uid}")
                        return uid
                    buffer = ""
            time.sleep(0.1)

        print("[HOST] Timeout waiting for UID.")
        return None

    except serial.SerialException as e:
        print(f"[HOST] Serial error: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 serial_enroll.py <user_id> <user_name> <serial_port>")
        sys.exit(1)

    uid = communicate_with_esp32(sys.argv[1], sys.argv[2], sys.argv[3])
    sys.exit(0 if uid else 1)
