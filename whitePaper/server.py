import websockets
import asyncio
import json
from .colorString import colorString
# from .log.log import LogSet
from .Log import Warn,Info,Error



class Server():
    def __init__(self):
        self.addr = None
        self.handlers = {}

    async def handler(self,ws):
        self.clientIP = ws.remote_address[0]
        if self.clientIP == '::1': self.clientIP = 'localhost'

        self.log.INFO(f"접속: {self.clientIP}")
        async for message in ws:  
            msg_locads = json.loads(message)
            TYPE = msg_locads['code']
            DATA = msg_locads['data']
            # print(DATA)

            if TYPE in list(self.handlers.keys()):
                # print(self.handlers[TYPE])
                self.handlers[TYPE](ws,message)

        Info(f'접속종료: {self.clientIP}')


    def recv(self, _msg=None):
        def decorator(func):
            if _msg != None:
                self.handlers[_msg] = func
            return func
        return decorator
    

    def open(self,addr):
        self.addr = addr
        async def opener(addr):
            async with websockets.serve(
            self.handler,
            addr[0],
            addr[1],
            compression=None
            ):
                self.log.INFO(f"{colorString('paper server started on',(50,255,50))} {colorString(f'ws://{addr[0]}:{addr[1]}',(252,70,140))}")
                await asyncio.Event().wait()
                await asyncio.Future()

        try:
            asyncio.run(opener(addr))
        except KeyboardInterrupt:
            self.log.ERROR("키보드 인터럽트 서버 강제종료")

