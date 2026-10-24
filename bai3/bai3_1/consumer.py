"""Nhom 16: nhan JSON, hien thi nhiet do va do am, ACK sau xu ly."""
import json
import math
import signal
import threading

import pika

from common import QUEUE_NAME, close, connect, declare_queue, log

stopping = threading.Event()


def parse_telemetry(body):
    payload = json.loads(body.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Payload phai la JSON object")
    values = []
    for field in ("temperature", "humidity"):
        value = payload.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field} phai la so")
        if not math.isfinite(value):
            raise ValueError(f"{field} phai huu han")
        values.append(value)
    if not 0 <= values[1] <= 100:
        raise ValueError("humidity phai nam trong 0..100")
    return values


def on_message(channel, method, properties, body):
    try:
        temperature, humidity = parse_telemetry(body)
    except (ValueError, UnicodeDecodeError, OverflowError) as exc:
        log.error("JSON ERROR | %s | payload=%r | continuing", exc, body[:200])
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return
    log.info("RECEIVED | queue=%s | temperature=%s C | humidity=%s %% | redelivered=%s",
             QUEUE_NAME, temperature, humidity, method.redelivered)
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stopping.set())
    while not stopping.is_set():
        connection = None
        try:
            connection = connect()
            channel = connection.channel()
            declare_queue(channel)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message,
                                  auto_ack=False)
            log.info("CONSUMER waiting | queue=%s | manual ACK", QUEUE_NAME)
            while not stopping.is_set():
                connection.process_data_events(time_limit=1)
        except (pika.exceptions.AMQPError, OSError) as exc:
            log.warning("CONSUMER connection error: %s; retry in 5s", type(exc).__name__)
            stopping.wait(5)
        finally:
            close(connection)
    log.info("CONSUMER stopped")


if __name__ == "__main__":
    main()
