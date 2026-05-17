import websockets
from ..NewId import NewId
import time

class ClientObj():
    def __init__(self,websc:websockets.ServerConnection):
        self.connectTime = time.time()
        self.address = websc.remote_address
        self.websc = websc
        self.id = NewId()
        self.loginUser = None
        self.sendReserve = []

    def addressGet(self):
        addr = list(self.address)
        if self.address[0] == '::1': addr[0] = 'localhost'
        return addr

    async def send(self,code: str | int, data:dict):
        if code == None or data == None:
            raise Exception("WhitePaper: 코드혹은 데이터가 없습니다")
        self.sendReserve.append(json.dumps({'code':code,'data':data}))
        return True

    async def _send_(self):
        for i in self.sendReserve:
            await self.websc.send(i)
        self.sendReserve = []