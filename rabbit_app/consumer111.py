import logging

from kombu import Connection
from rabbit_app import message_bus

logging.basicConfig(level=logging.INFO)


class MessageBus:
    settings = message_bus.settings
    connection = Connection(settings.BROKER_URL)
    message_bus.broker_scheme.declare(connection)

    consumer = message_bus.create_consumer(
        connection
    )

    consumer_with_routing_key = message_bus.create_consumer_with_routing_key(
        connection
    )


#MessageBus.consumer.run()
MessageBus.consumer_with_routing_key.run()
