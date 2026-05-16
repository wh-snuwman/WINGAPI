import websockets
import asyncio
import json
import time
from .ColorString import ColorString as CorlStr
from .Log import Warn,Info,Error
from copy import deepcopy
from .NewId import NewId


BASIC_RIGHT = ['visitor'] # 처음접속시 기본적으로 지급하는 역할
CLIENTS = {} # 현재 접속해있는 클라이언트 목록


class ClientObj():
    def __init__(self):
        self.connectTime = time.time()
        self.ip : str
        self.id = NewId()
        self.right = deepcopy(BASIC_RIGHT)
        self.role : str




class Server():
    def __init__(self):
        self.addr = None
        self.handlers = {}

    async def handler(self,ws):
        self.clientIP = ws.remote_address[0]
        if self.clientIP == '::1': self.clientIP = 'localhost'

        Info(f"접속: {self.clientIP}")
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
                Info(f"{CorlStr('paper server started on',(50,255,50))} {CorlStr(f'ws://{addr[0]}:{addr[1]}',(252,70,140))}")
                await asyncio.Event().wait()
                await asyncio.Future()

        try:
            asyncio.run(opener(addr))
        except KeyboardInterrupt:
            Error("키보드 인터럽트 서버 강제종료")

    