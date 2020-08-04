# Copyright: Copyright 2020, CryptoQuant
# License: Simplified BSD License
# Author: Denver Lu
# Email: danfeng.l@gmail.com

"""
This service mainly deals with future related market data from Deribit API.
It collects market data via websocket, and then publish it through 0mq to subscribers.
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import json
import time
import asyncio
import websockets
import zmq.asyncio
from base import ServiceState, ServiceBase, start_service
from config import SYMBOL, DERIBIT_API_WEBSOCKET


active_channels = set()
hourly_updated = False


MSG_SUBSCRIBE_ID = 3600
subscribe = {
    "jsonrpc": "2.0",
    "id": MSG_SUBSCRIBE_ID,
    "method": "public/subscribe",
    "params": {
        "channels": [
        ]
    }
}

MSG_PRIVATE_SUBSCRIBE_ID = 4235
private_subscribe = {
    "jsonrpc": "2.0",
    "id": MSG_PRIVATE_SUBSCRIBE_ID,
    "method": "private/subscribe",
    "params": {
        "channels": [
        ]
    }
}

MSG_UNSUBSCRIBE_ID = 8691
unsubscribe = {
    "jsonrpc": "2.0",
    "id": MSG_UNSUBSCRIBE_ID,
    "method": "public/unsubscribe",
    "params": {
        "channels": []
    }
}

MSG_HEARTBEAT_ID = 110
heartbeat = {
    "method": "public/set_heartbeat",
    "params": {
        "interval": 10
    },
    "jsonrpc": "2.0",
    "id": MSG_HEARTBEAT_ID
}

MSG_TEST_ID = 8212
test = {
    "jsonrpc": "2.0",
    "id": MSG_TEST_ID,
    "method": "public/test",
    "params": {}
}

MSG_INSTRUMENTS_ID = 7617
instruments = {
    "jsonrpc": "2.0",
    "id": MSG_INSTRUMENTS_ID,
    "method": "public/get_instruments",
    "params": {
        "currency": SYMBOL,
        "kind": "future",
        "expired": False
    }
}


class DeribitMD(ServiceBase):
    """ Service of handlering Deribit market data. """
    def __init__(self, sid, logger_name):
        ServiceBase.__init__(self, logger_name)
        self.sid = sid
        # zmq PUB socket for publishing market data
        self.pubserver = self.ctx.socket(zmq.PUB)
        self.pubserver.bind('tcp://*:9050')

    async def pub_msg(self):
        """ Get market data from API websocket, then pub it to zmq. """
        try:
            async with websockets.connect(DERIBIT_API_WEBSOCKET) as websocket:
                self.logger.info('Connected to deribit websocket server')
                global active_channels, hourly_updated
                # set heartbeat to keep alive
                await websocket.send(json.dumps(heartbeat))
                await websocket.recv()

                # get instruments and then update channels
                await websocket.send(json.dumps(instruments))
                response = json.loads(await websocket.recv())
                for i in response['result']:
                    self.pubserver.send_string(json.dumps({'type': 'instrument',
                                                           'data': i}))
                    for j in ('trades', 'ticker', 'book'):
                        active_channels.add('.'.join([j, i['instrument_name'], 'raw']))
                subscribe['params']['channels'] = list(active_channels)
                await websocket.send(json.dumps(subscribe))

                hourly_updated = True
                last_heartbeat = time.time()
                while websocket.open and self.state == ServiceState.started:
                    # check heartbeat to see if websocket is broken
                    if time.time() - last_heartbeat > 30:
                        raise websockets.exceptions.ConnectionClosedError(
                            1003, 'Serverside heartbeat stopped')
                    # update instruments every hour
                    if time.gmtime().tm_min == 5 and not hourly_updated:
                        self.logger.info('Fetching instruments hourly ******')
                        await websocket.send(json.dumps(instruments))
                        hourly_updated = True
                    elif time.gmtime().tm_min == 31 and hourly_updated:
                        hourly_updated = False
                    else:
                        pass

                    response = json.loads(await websocket.recv())
                    # need response heartbeat to keep alive
                    if response.get('method', '') == 'heartbeat':
                        if response['params']['type'] == 'test_request':
                            last_heartbeat = time.time()
                            await websocket.send(json.dumps(test))
                        else:
                            pass
                    elif response.get('id', '') == MSG_INSTRUMENTS_ID:
                        new_channels = set()
                        for i in response['result']:
                            for j in ('trades', 'ticker', 'book'):
                                new_channels.add('.'.join([j, i['instrument_name'], 'raw']))
                        if len(new_channels.difference(active_channels)) > 0:
                            self.logger.info('There are new channels as following:')
                            self.logger.info(str(new_channels.difference(active_channels)))
                            subscribe['params']['channels'] = list(new_channels)
                            await websocket.send(json.dumps(subscribe))
                            unsubscribe['params']['channels'] = list(active_channels.difference(new_channels))
                            await websocket.send(json.dumps(unsubscribe))
                            new_instruments = set()
                            for i in new_channels.difference(active_channels):
                                new_instruments.add(i.split('.')[1])
                            for i in response['result']:
                                if i['instrument_name'] in new_instruments:
                                    self.pubserver.send_string(json.dumps({'type': 'instrument',
                                                                           'data': i}))
                            active_channels = new_channels
                    elif response.get('params', ''):
                        if response['params']['channel'].startswith('trades'):
                            for i in response['params']['data']:
                                self.pubserver.send_string(json.dumps({'type': 'trade',
                                                                       'data': i}))
                        elif response['params']['channel'].startswith('ticker'):
                            self.pubserver.send_string(
                                json.dumps({'type': 'quote',
                                            'data': response['params']['data']}))
                        elif response['params']['channel'].startswith('book'):
                            self.pubserver.send_string(
                                json.dumps({'type': 'book',
                                            'data': response['params']['data']}))
                        else:
                            pass
                    else:
                        pass
                else:
                    if self.state == ServiceState.started:
                        self.logger.info('websocket is not open')
                        await self.pub_msg()
        # except websockets.exceptions.ConnectionClosedError:
        #     await self.pub_msg()
        except Exception as e:
            self.logger.exception(e)
            await asyncio.sleep(1)
            await self.pub_msg()

    async def run(self):
        """ Where the service does its job, and called by start func. """
        if self.state == ServiceState.started:
            self.logger.error('tried to run service, but state is %s', self.state)
        else:
            self.state = ServiceState.started
            await self.pub_msg()


if __name__ == '__main__':
    service = DeribitMD('deribit-future-md', 'deribit-future-md')
    start_service(service, {})
