import json
import time
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
TOPIC = "it4735/nhom16/telemetry"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        raise RuntimeError(f"Connection refused: {reason_code}")
    client.subscribe(TOPIC)


def on_subscribe(client, userdata, mid, reason_codes, properties):
    if any(code.is_failure for code in reason_codes):
        raise RuntimeError("Broker rejected the subscription")
    print("SUBSCRIBED", TOPIC, flush=True)


def on_message(client, userdata, message):
    try:
        data = json.loads(message.payload)
        temperature, humidity = data["temperature"], data["humidity"]
        if any(type(value) not in (int, float) for value in (temperature, humidity)):
            raise ValueError("Temperature and humidity must be numbers")
        print(time.strftime("[%H:%M:%S]"), message.topic,
              f"| Temperature: {temperature} C | Humidity: {humidity} %", flush=True)
    except (ValueError, KeyError, TypeError) as error:
        print("Invalid data:", error, flush=True)


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    try:
        client.connect(BROKER, 1883)
        client.loop_forever()
    except KeyboardInterrupt:
        print("Subscriber stopped")
    except (OSError, RuntimeError) as error:
        print("ERROR:", error)
        return 1
    finally:
        client.disconnect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
