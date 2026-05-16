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
USERS = {} # 저장된 유저 데이터. 데이터베이스와 주기적으로 동기화됨 

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


class UserObj():
    def __init__(self):
        self.nickname : str
        self.tag = []
        self.role : str
        self.right : set
        self.id = NewId()
    
    def giveRight(self,r):
        self.right.add(r)

    def depriveRight(self,r):
        self.right.remove(r)

    def setRole(self,r):
        self.role = r

    def role_get(self,r):
        self.role = r

    def right_get(self):
        return self.right


class Server():
    def __init__(self):
        self.addr = None
        self.handlers = {}


    def _isSysMsg(self,msg):
        return (len(msg) > 5) and msg[0:5] == 'wing:'
        
    def _SysMsgEdit(self,msg):
        return msg[5:]



    async def handler(self,websc):
        global USERS,CLIENTS
        obj = ClientObj(websc)
        self.address = obj.addressGet() 
        self.clientIP = self.address[0] # ip

        Info(f"접속: {self.clientIP}")
        async for data in websc:  
            msgLoads = json.loads(data)
            CODE = msgLoads['code']
            DATA = msgLoads['data']
            if self._isSysMsg(CODE):
                CODE = self._SysMsgEdit(CODE)
                
                if CODE == 'signup':
                    NICKNAME = DATA['nickname']
                    PASSWORD = DATA['password']
                    if NICKNAME in USERS:
                        await obj.send(code='wing:signup',data={'state':'repeatNickname','signup':False})
                        continue
                    if len(PASSWORD) < 4:
                        await obj.send(code='wing:signup',data={'state':'shortPassword','signup':False})
                        continue
                        
                    # USERS[NICKNAME] =
                    await obj.send(code='wing:signup',data={'state':'sueccess','signup':True})
                
                await obj._send_()
                continue

            if CODE in list(self.handlers.keys()):
                await self.handlers[CODE](obj,CODE,DATA)

            await obj._send_()
            

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

    