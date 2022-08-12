import json
import pika
import time
import logging
from pika.exceptions import AMQPConnectionError
from core.settings import (RABBIT_CONNECTION, RABBIT_PORT,
                           RABBIT_PW, RABBIT_USER, PUBLISH_QUEUE)

logger = logging.getLogger(__name__)


class PikaClient:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __del__(self):
        PikaClient.__instance = None

    def __init__(self):

        self.credentials = pika.PlainCredentials(username=RABBIT_USER, password=RABBIT_PW)

        while True:
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=RABBIT_CONNECTION,
                    port=RABBIT_PORT,
                    credentials=self.credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                ))
                if self.connection.is_open:
                    logger.info("Connection established")
                    break
            except AMQPConnectionError as error:
                logger.warning('No connection yet:', error.__class__.__name__)
                time.sleep(5)

        self.channel = self.connection.channel()
        self.queue = PUBLISH_QUEUE
        self.channel.queue_declare(self.queue)

    def publish(self, method, body):
        properties = pika.BasicProperties(method)
        self.channel.basic_publish(exchange='', routing_key='innotter',
                                   body=str.encode(json.dumps(body)),
                                   properties=properties)
        logger.info("Message published")
