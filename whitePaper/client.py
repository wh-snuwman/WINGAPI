import websockets
import asyncio
import json
import time

'''
code: 메세지타입저장
cover: 부가데이터 및 메세지 메타정보
data: 실제데이터 저장
'''


class Client():
    def  __init__(self):
        self.websc = None
        self.mainFunc = None
    
    async def send(self,code:str | int,data:dict):
        dataDumps = json.dumps(data)
        sendData = {
            'code':code,
            'cover': {
                'sendTime':time.time(),
                'length': len(dataDumps),
            },
            'data':dataDumps,
        }
        await self.websc.send(json.dumps(sendData))
        return sendData

    def main(self):
        def _main(func):
            self.mainFunc = func
            return func
        return _main


    async def recv(self,msg:str):
        def deco(func):
            return func
        return deco

    def connect(self,addr):
        async def _run(addr):
            async with websockets.connect('ws://localhost:3000') as websc:
                self.websc = websc
                await self.mainFunc()

        

        try:
            asyncio.run(_run(addr))
        except KeyboardInterrupt:
            pass                    

