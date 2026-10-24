"""Nhom 16: gui JSON nhiet do, do am qua default exchange moi 5 giay."""
import json
import math
import os
import random
import signal
import threading

import pika

from common import QUEUE_NAME, close, connect, declare_queue, log

stopping = threading.Event()


def main():
    interval = float(os.getenv("INTERVAL_SECONDS", "5"))
    if not math.isfinite(interval) or interval <= 0:
        raise ValueError("INTERVAL_SECONDS phai la so duong huu han")
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stopping.set())

    sent = 0
    while not stopping.is_set():
        connection = None
        try:
            connection = connect()
            channel = connection.channel()
            declare_queue(channel)
            channel.confirm_delivery()
            log.info("PRODUCER connected | queue=%s | interval=%ss", QUEUE_NAME, interval)
            while not stopping.is_set():
                payload = {"temperature": round(random.uniform(23, 35), 1),
                           "humidity": round(random.uniform(40, 80), 1)}
                body = json.dumps(payload, allow_nan=False).encode("utf-8")
                channel.basic_publish(
                    exchange="",  # Default exchange: routing key chinh la ten queue.
                    routing_key=QUEUE_NAME,
                    body=body,
                    properties=pika.BasicProperties(
                        content_type="application/json", content_encoding="utf-8",
                        delivery_mode=2),
                    mandatory=True,
                )
                sent += 1
                log.info("SENT #%s | queue=%s | %s", sent, QUEUE_NAME, body.decode())
                # Xu ly heartbeat trong luc cho, dung nhanh khi docker compose stop.
                remaining = interval
                while remaining > 0 and not stopping.is_set():
                    step = min(remaining, 0.5)
                    connection.sleep(step)
                    remaining -= step
        except (pika.exceptions.AMQPError, OSError) as exc:
            log.warning("PRODUCER connection error: %s; retry in 5s", type(exc).__name__)
            stopping.wait(5)
        finally:
            close(connection)
    log.info("PRODUCER stopped | sent=%s", sent)


if __name__ == "__main__":
    main()
