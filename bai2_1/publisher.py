import json
import random
import threading
import time
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
TOPIC = "it4735/nhom16/telemetry"


def main():
    connected = threading.Event()

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            connected.set()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    try:
        client.connect(BROKER, 1883)
        client.loop_start()
        if not connected.wait(10):
            raise TimeoutError("Could not connect to broker")

        while True:
            payload = json.dumps({
                "temperature": round(random.uniform(23, 32), 1),
                "humidity": round(random.uniform(40, 70), 1),
            })
            result = client.publish(TOPIC, payload)
            result.wait_for_publish(timeout=10)
            if not result.is_published():
                raise TimeoutError("Message publish timed out")
            print(time.strftime("[%H:%M:%S]"), "PUBLISHED", payload, flush=True)
            time.sleep(5)
    except KeyboardInterrupt:
        print("Publisher stopped")
    except (OSError, RuntimeError) as error:
        print("ERROR:", error)
        return 1
    finally:
        client.disconnect()
        client.loop_stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
