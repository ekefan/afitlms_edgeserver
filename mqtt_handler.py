import asyncio
import gmqtt
import json
import contextlib as ctxlib
from datetime import datetime
import sqlite3
from database import get_db_connection
from models import LectureSessionBase, StudentAttendanceRecordBase


MQTT_BROKER_HOST = 'localhost'
MQTT_BROKER_PORT = 1883
MQTT_CLIENT_ID = 'cs_edge_mqtt_client'

LECTURE_SESSION_TOPIC = "cs/lecture/session"
ATTENDANCE_TOPIC = "cs/attendance"

mqtt_client: gmqtt.Client = None

def on_connect(client, flags, rc, properties):
    """Callback for when the MQTT client connects to the broker."""
    print(f"MQTT: Connected to broker with result code: {rc}")
    # Subscribe to required topics upon successful connection
    client.subscribe(LECTURE_SESSION_TOPIC, qos=1)
    client.subscribe(ATTENDANCE_TOPIC, qos=1)
    print(f"MQTT: Subscribed to topics: {LECTURE_SESSION_TOPIC}, {ATTENDANCE_TOPIC}")


def on_message(client, topic, payload, qos, prop):
    print(f'still working on this part:\nclient: {client}\ntopic: {topic}\npayload: {payload}\nqos: {qos}\nprop: {prop}')
# handle on_message received for subscriptions

async def start_mqtt_client():
    """Initializes and connects the MQTT client"""
    global mqtt_client
    mqtt_client = gmqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message


    mqtt_client.on_disconnect = lambda client, packet, exc: print(f"MQTT: Disconnected: {exc}")
    mqtt_client.on_subscribe = lambda client, mid, qos, properties: print(f"MQTT: SUBSCRIBED MID={mid}, QOS={qos}, Prop={properties}")

    try:
        print(f"MQTT: Attempting to connect to broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}...")
        await mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
        print("MQTT: Client connection initiated.")
        # TODO:
        # Keep the client running by awaiting a long-running task if needed,
        # but the lifespan management will handle the main loop.
    except Exception as e:
        print(f"MQTT ERROR: Failed to connect to broker: {e}")
        # You might want to implement a reconnection strategy here for robustness

async def stop_mqtt_client():
    """Disconnects the MQTT client gracefully."""
    global mqtt_client
    if mqtt_client:
        await mqtt_client.disconnect()
        print("MQTT: Client disconnected.")
