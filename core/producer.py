import json
import pika
from settings import (RABBIT_CONNECTION, RABBIT_PORT,
                      RABBIT_PW, RABBIT_USER, PUBLISH_QUEUE)


credentials = pika.PlainCredentials(username=RABBIT_USER, password=RABBIT_PW)

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=RABBIT_CONNECTION,
    port=RABBIT_PORT,
    credentials=credentials,
    heartbeat=600,
    blocked_connection_timeout=300
))

channel = connection.channel()

channel.queue_declare(PUBLISH_QUEUE)


def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='innotter',
                          body=str.encode(json.dumps(body)),
                          properties=properties)
    print("Message is published")


publish("lala", {"hasfea": "stre"})

publish("lala", {"dsd": "asda"})
