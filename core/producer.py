import json
import pika
import time
from pika.exceptions import AMQPConnectionError
from core.settings import (RABBIT_CONNECTION, RABBIT_PORT,
                           RABBIT_PW, RABBIT_USER, PUBLISH_QUEUE)


credentials = pika.PlainCredentials(username=RABBIT_USER, password=RABBIT_PW)

while True:
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=RABBIT_CONNECTION,
            port=RABBIT_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        ))
        if connection.is_open:
            print('OK')
            break
    except AMQPConnectionError as error:
        print('No connection yet:', error.__class__.__name__)
        time.sleep(5)

channel = connection.channel()

channel.queue_declare(PUBLISH_QUEUE)


def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='innotter',
                          body=str.encode(json.dumps(body)),
                          properties=properties)
    print("Message is published")
