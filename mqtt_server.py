# mqtt_server.py
import json
import paho.mqtt.client as mqtt
from data_store import courses

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

def on_connect(client, userdata, flags, rc):
    print("MQTT Connected")
    client.subscribe("esp32/request/course_codes")
    client.subscribe("esp32/request/attendance_info")
    client.subscribe("esp32/record/attendance")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = json.loads(msg.payload.decode())

    if topic == "esp32/request/course_codes":
        level, faculty, dept = payload["level"], payload["faculty"], payload["dept"]
        filtered = list(courses.keys())  # Add filtering logic here
        client.publish("esp32/response/course_codes", json.dumps(filtered))

    elif topic == "esp32/request/attendance_info":
        course_code = payload["course_code"]
        course = courses.get(course_code, {})
        client.publish("esp32/response/attendance_info", json.dumps(course))

    elif topic == "esp32/record/attendance":
        course_code = payload["course_code"]
        updates = payload["updates"]
        if course_code in courses:
            courses[course_code]["lecturer"]["attended"] = updates["lecturer"]
            for update in updates["students"]:
                for student in courses[course_code]["students"]:
                    if student["name"] == update["name"]:
                        student["attended"] = update["attended"]

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_forever()
