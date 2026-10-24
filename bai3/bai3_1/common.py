"""Cau hinh dung chung cua producer va consumer, AMQP 0-9-1."""
import logging
import os

import pika

QUEUE_NAME = os.getenv("QUEUE_NAME", "it4735.nhom16.telemetry")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logging.getLogger("pika").setLevel(logging.WARNING)
log = logging.getLogger("nhom16")


def connect():
    """Docker DNS: rabbitmq; localhost neu chay Python ngoai container."""
    return pika.BlockingConnection(pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "localhost"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        credentials=pika.PlainCredentials(
            os.getenv("RABBITMQ_USER", "nhom16"),
            os.environ["RABBITMQ_PASSWORD"],
        ),
        heartbeat=30,
        blocked_connection_timeout=30,
        socket_timeout=5,
        connection_attempts=3,
        retry_delay=2,
    ))


def declare_queue(channel):
    # Cung ten va cung thuoc tinh o ca hai chuong trinh.
    return channel.queue_declare(queue=QUEUE_NAME, durable=True)


def close(connection):
    if connection is not None and connection.is_open:
        try:
            connection.close()
        except pika.exceptions.AMQPError:
            pass
