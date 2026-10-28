"""Validate JSON, display fields and ACK only after successful processing."""
import argparse
import pika
from common import open_channel, parse_payload, queue_name, retry_notice


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-messages', type=int, default=0)
    args = parser.parse_args()
    received = 0
    while True:
        connection = None
        try:
            connection, channel = open_channel()
            channel.basic_qos(prefetch_count=1)

            def callback(ch, method, properties, body):
                nonlocal received
                try:
                    data = parse_payload(body)
                except (ValueError, UnicodeError, RecursionError) as error:
                    print(f'JSON ERROR type={type(error).__name__}; rejected; continuing', flush=True)
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                else:
                    print('RECEIVED ' + ' '.join(f'{k}={data[k]}' for k in
                          ('DeviceId', 'packet_no', 'temperature', 'humidity')) +
                          f' persistent={properties.delivery_mode == 2}', flush=True)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                received += 1
                if args.max_messages and received >= args.max_messages:
                    ch.stop_consuming()

            channel.basic_consume(queue=queue_name(), on_message_callback=callback, auto_ack=False)
            print(f'WAITING queue={queue_name()} manual_ack=True', flush=True)
            channel.start_consuming()
            return
        except pika.exceptions.AMQPError as error:
            retry_notice(error)
        finally:
            if connection and connection.is_open:
                connection.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Consumer stopped', flush=True)
