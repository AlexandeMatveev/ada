import json
from typing import Callable

import aio_pika
from aio_pika import connect_robust, Message, ExchangeType

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        self._connected = False

    async def connect(self):
        self.connection = await connect_robust(
            host="rabbitmq",
            port=5672,
            login="rabbit_user",
            password="rabbit_pass",
            virtualhost="/"
        )
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            "app_events", ExchangeType.TOPIC, durable=True
        )
        self._connected = True
        print("Connected to RabbitMQ")

    async def publish(self, routing_key: str, data: dict):
        if not self._connected:
            await self.connect()
        message_body = json.dumps(data, default=str).encode()
        message = Message(
            message_body,
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await self.exchange.publish(message, routing_key=routing_key)

    async def consume(self, routing_key: str, queue_name: str, callback: Callable):
        if not self._connected:
            await self.connect()
        queue = await self.channel.declare_queue(queue_name, durable=True)
        await queue.bind(self.exchange, routing_key)

        async def wrapped_callback(message: aio_pika.IncomingMessage):
            async with message.process():
                body = json.loads(message.body.decode())
                await callback(body)

        await queue.consume(wrapped_callback)

rabbit_client = RabbitMQClient()