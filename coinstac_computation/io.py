import asyncio as _asyncio
import json as _json
import websockets as _ws
import traceback as _tb
from datetime import datetime as _dt


class COINSTACPyNode:
    _VALID_NODES_ = ['remote', 'local']

    def __init__(self, name):
        self.cache = {}
        self.input = {}
        self.state = {}
        self.output = {}
        self._msg = {}
        self._node = name
        assert self._node in COINSTACPyNode._VALID_NODES_, "Not a valid node name"

    def _recv(self, websocket):
        msg = await websocket.recv()
        try:
            self._msg = _json.loads(msg)
            self.input = self._msg['data']['input']
            self.state = self._msg['data']['state']
        except:
            _tb.print_exc()
            await websocket.close(1011, 'JSON data parse failed')

    def compute(self):
        raise NotImplementedError('Must be implemented.')

    async def _run(self, websocket, path):
        self._recv(websocket)
        if self._msg['mode'] in self._VALID_NODES_:
            try:
                start = _dt.now()
                output = await _asyncio.get_event_loop().run_in_executor(None, self.compute)
                print(f'{self._node} exec time:', (_dt.now() - start).total_seconds())
                await websocket.send(_json.dumps({'type': 'stdout', 'data': output, 'end': True}))
            except Exception as e:
                _tb.print_exc()
                print('local data:', self._msg['data'])
                await websocket.send(_json.dumps({'type': 'stderr', 'data': str(e), 'end': True}))
        else:
            await websocket.close()

    def start(self):
        start_server = _ws.serve(self._run, '0.0.0.0', 8881)
        print("Python microservice started on 8881")
        _asyncio.get_event_loop().run_until_complete(start_server)
        _asyncio.get_event_loop().run_forever()
