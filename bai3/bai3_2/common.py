"""Shared AMQP configuration. Never log credentials or connection URLs."""
import json
import math
import os
import time

import pika


def queue_name():
    student_id = os.environ['MSSV']
    if not student_id.isdigit():
        raise ValueError('MSSV must contain digits only')
    return f'it4735.{student_id}.telemetry' + os.getenv('QUEUE_SUFFIX', '')


def connect():
    params = pika.ConnectionParameters(
        host=os.getenv('RABBITMQ_HOST', 'localhost'),
        port=int(os.getenv('RABBITMQ_PORT', '5672')),
        credentials=pika.PlainCredentials(
            os.environ['RABBITMQ_USER'], os.environ['RABBITMQ_PASSWORD']),
        heartbeat=30, blocked_connection_timeout=30,
        socket_timeout=10, connection_attempts=1)
    return pika.BlockingConnection(params)


def open_channel():
    conn = connect()
    channel = conn.channel()
    channel.queue_declare(queue=queue_name(), durable=True)
    return conn, channel


def publish(channel, data):
    channel.basic_publish(
        exchange='', routing_key=queue_name(),
        body=json.dumps(data, ensure_ascii=False, allow_nan=False).encode('utf-8'),
        mandatory=True,
        properties=pika.BasicProperties(
            delivery_mode=2, content_type='application/json', content_encoding='utf-8'))


def parse_payload(body):
    data = json.loads(body.decode('utf-8'))
    if not isinstance(data, dict):
        raise ValueError('JSON must be an object')
    for key in ('DeviceId', 'packet_no'):
        if type(data.get(key)) is not int or data[key] < 0:
            raise ValueError(f'{key} must be a nonnegative integer')
    for key in ('temperature', 'humidity'):
        value = data.get(key)
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f'{key} must be a finite number')
    return data


def retry_notice(error):
    print(f'CONNECTION ERROR type={type(error).__name__}; retry in 3s', flush=True)
    time.sleep(3)
