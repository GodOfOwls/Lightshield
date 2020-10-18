import asyncio
import os
import aiohttp
import logging
import aio_pika
from aio_pika import ExchangeType, Message, DeliveryMode
import pickle
import datetime

class RabbitManager:

    def __init__(self, incoming=None, exchange=None, outgoing=()):
        self.logging = logging.getLogger("RabbitMQ")
        self.logging.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(
            logging.Formatter('%(asctime)s [RabbitMQ] %(message)s'))
        self.logging.addHandler(handler)

        self.server = os.environ['SERVER']
        self.streamID = os.environ['STREAM']
        self.max_buffer = int(os.environ['MAX_TASK_BUFFER'])

        self.outgoing = outgoing

        self.incoming = incoming
        
        self.blocked = True
        self.stopped = False
        self.connection = None
        self.channel = None
        self.exchange = self.server + "_" + exchange
        self.empty_response = None

    def shutdown(self) -> None:
        self.stopped = True

    async def connect(self, prefetch):
        self.connection = await aio_pika.connect_robust(
            "amqp://guest:guest@rabbitmq/", loop=asyncio.get_running_loop())

    async def init(self, prefetch=50):
        self.empty_response = datetime.datetime.now()
        await self.connect(prefetch)
        headers = {
            'content-type': 'application/json'
        }
        while not self.stopped:
            async with aiohttp.ClientSession(auth=aiohttp.BasicAuth("guest", "guest")) as session:
                async with session.get(
                        'http://rabbitmq:15672/api/queues', headers=headers) as response:
                    resp = await response.json()
                    queues = {entry['name']: entry for entry in resp}
                    missing = False
                    for queue in self.outgoing:
                        if self.server + "_" + queue not in queues:
                            self.logging.info("Queue %s not initialized yet. Waiting.", queue)
                            missing = True
                            break
            await asyncio.sleep(1)
            if not missing:
                return

    async def check_full(self) -> None:
        """Check if the size of any of the queues is above wanted levels."""
        headers = {
            'content-type': 'application/json'
        }
        self.logging.info("Initiating buffer checker")
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth("guest", "guest")) as session:
            while not self.stopped:
                async with session.get(
                        'http://rabbitmq:15672/api/queues', headers=headers) as response:
                    resp = await response.json()
                    queues = {entry['name']: entry['messages'] for entry in resp}
                    was_blocked = self.blocked
                    self.blocked = False
                    queue_identifier = self.server + "_" + self.streamID
                    for queue in queues:
                        if queue.startswith(queue_identifier):
                            try:
                                
                                if int(queues[queue]) > self.max_buffer:
                                    if not was_blocked:
                                        self.logging.info("Queue %s is too full [%s/%s]", 
                                                queue, queues[queue], self.max_buffer)
                                    self.blocked = True

                            except Exception as err:
                                print(err)
                                raise err
                    if was_blocked and not self.blocked:
                        self.logging.info("Blocker released.")
                await asyncio.sleep(1)

    async def get_task(self):
        channel = await self.connection.channel()
        await channel.set_qos(prefetch_count=50)
        queue = await channel.declare_queue(
            name=self.server + "_" + self.incoming,
            durable=True,
            robust=True
        )
        try:
            if (datetime.datetime.now() - self.empty_response).total_seconds() < 2:
                return None
            return await queue.get(timeout=3)
        except Exception as err:
            self.empty_response = datetime.datetime.now()
            self.logging.info("Error received: %s: %s", err.__class__.__name__, err)
            return None
        finally:
            channel.close()

    async def add_task(self, message) -> None:
        channel = await self.connection.channel()
        exchange = await channel.declare_exchange(
            name=self.exchange,
            durable=True,
            type=ExchangeType.TOPIC,
            robust=True)
        try:
            await exchange.publish(
                Message(body=pickle.dumps(message),
                        delivery_mode=DeliveryMode.PERSISTENT),
                routing_key="")
        finally:
            channel.close()
