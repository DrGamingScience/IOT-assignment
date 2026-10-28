"""Periodic simulated telemetry with persistence and publisher confirms."""
import argparse
import os
from pathlib import Path
import random

import pika
from common import open_channel, publish, queue_name, retry_notice


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=0, help='0 means continuous')
    parser.add_argument('--interval', type=float, default=float(os.getenv('INTERVAL_SECONDS', '5')))
    parser.add_argument('--start', type=int, default=126)
    args = parser.parse_args()
    if args.count < 0 or args.interval <= 0 or args.start < 0:
        parser.error('count/start must be nonnegative and interval positive')
    state = Path(os.environ['STATE_FILE']) if os.getenv('STATE_FILE') else None
    packet = int(state.read_text()) if state and state.exists() else args.start
    sent = 0
    pending = None
    while args.count == 0 or sent < args.count:
        connection = None
        try:
            connection, channel = open_channel()
            channel.confirm_delivery()
            print(f'CONNECTED producer queue={queue_name()} durable=True persistent=True', flush=True)
            while args.count == 0 or sent < args.count:
                if pending is None:
                    pending = {'DeviceId': 11, 'packet_no': packet,
                               'temperature': round(random.uniform(23, 35), 1),
                               'humidity': round(random.uniform(40, 80), 1)}
                publish(channel, pending)
                print(f'SENT packet_no={packet} data={pending}', flush=True)
                packet += 1
                if state:
                    state.parent.mkdir(parents=True, exist_ok=True)
                    temp = state.with_suffix('.tmp')
                    temp.write_text(str(packet), encoding='utf-8')
                    temp.replace(state)
                pending = None
                sent += 1
                if args.count == 0 or sent < args.count:
                    connection.sleep(args.interval)
        except pika.exceptions.AMQPError as error:
            # An interrupted confirm can cause a duplicate when retried.
            # Reuse the same packet number rather than silently skipping it.
            retry_notice(error)
        finally:
            if connection and connection.is_open:
                connection.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Producer stopped', flush=True)
