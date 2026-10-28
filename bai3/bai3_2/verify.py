"""Integration checks on a separate disposable queue; main queue is untouched."""
import json
import os
import subprocess
import sys
import uuid
from common import open_channel, parse_payload, publish, queue_name


def main():
    os.environ['QUEUE_SUFFIX'] = '.verify.' + uuid.uuid4().hex[:10]
    connection, channel = open_channel()
    result = {'queue': queue_name(), 'checks': []}
    try:
        channel.confirm_delivery()
        subprocess.run([sys.executable, 'producer.py', '--count', '5', '--interval', '0.1'],
                       env={k: v for k, v in os.environ.items() if k != 'STATE_FILE'}, check=True, timeout=30)
        ready = channel.queue_declare(queue=queue_name(), passive=True).method.message_count
        assert ready == 5, ready
        result['checks'].append({'backlog_ready': ready, 'expected': 5})
        # Peek by get + NACK requeue; verify payload properties without discarding messages.
        method, properties, body = channel.basic_get(queue=queue_name(), auto_ack=False)
        assert properties.delivery_mode == 2 and properties.content_type == 'application/json'
        assert parse_payload(body)['packet_no'] == 126
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        result['checks'].append({'persistent': True, 'content_type': properties.content_type})
        channel.basic_publish(exchange='', routing_key=queue_name(), body=b'hello')
        publish(channel, {'DeviceId': 11, 'packet_no': 131, 'temperature': 30, 'humidity': 60})
        completed = subprocess.run([sys.executable, 'consumer.py', '--max-messages', '7'],
                                   capture_output=True, text=True, timeout=30, check=True)
        print(completed.stdout)
        import re
        numbers = [int(n) for n in re.findall(r'RECEIVED DeviceId=11 packet_no=(\d+)', completed.stdout)]
        assert numbers == list(range(126, 132)), numbers
        assert 'JSON ERROR' in completed.stdout
        assert completed.stdout.index('JSON ERROR') < completed.stdout.index('packet_no=131')
        assert channel.queue_declare(queue=queue_name(), passive=True).method.message_count == 0
        result['checks'].append({'received_packets': numbers, 'invalid_json_recovered': True, 'ready_after': 0})
        for bad in (b'[]', b'{}', b'null', b'\xff', b'{"DeviceId":true}',
                    b'{"DeviceId":11,"packet_no":1,"temperature":NaN,"humidity":60}'):
            try:
                parse_payload(bad)
                raise AssertionError(f'Accepted invalid input {bad!r}')
            except (ValueError, UnicodeError):
                pass
        result['status'] = 'PASS'
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        if channel.is_open:
            channel.queue_delete(queue=queue_name())
        if connection.is_open:
            connection.close()


if __name__ == '__main__':
    main()
