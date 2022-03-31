"""Pub-Sub helper module."""

import json
import pika
from pika import exceptions, PlainCredentials

from constants import BROKER_BLOCKING_TIMEOUT, GUEST_USER, LOCALHOST


class PubSubHelper:
    """Helper class for Pub-Sub.

    Refer to details on connection params:
    https://pika.readthedocs.io/en/stable/modules/parameters.html#connectionparameters

    Attributes
    ----------
    connection_params: pika.connection.ConnectionParameters
        Connection params
    connection: pika.adapters.blocking_connection.BlockingConnection
    channel: pika.adapters.blocking_connection.BlockingChannel

    """

    def __init__(self) -> None:
        """Instantiate."""
        self.connection_params = pika.ConnectionParameters(
            host=LOCALHOST,
            port=5672,
            blocked_connection_timeout=BROKER_BLOCKING_TIMEOUT,
            credentials=PlainCredentials(username=GUEST_USER, password=GUEST_USER),
        )
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()

    def setup_queue(self, queue_name: str) -> None:
        """Set up message queue for communication of results to user.

        Parameters
        ----------
        queue_name: str
            Unique name for queue.
        """
        try:
            self.channel.queue_declare(queue=queue_name)
        except exceptions.StreamLostError:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=queue_name)

    def send_message(
        self, queue_name: str, message_to_send: dict, user: str = ""
    ) -> None:
        """Publish messeage to the rabbitMQ broker.

        Parameters
        ----------
        queue_name: str
            Unique name for queue.
        message_to_send: dict
            Message to send via broker.
        user: str
            Name of user.
        """
        self.channel.basic_publish(
            user, routing_key=queue_name, body=json.dumps(message_to_send)
        )


pubsub_helper = PubSubHelper()
