import websockets
import asyncio
import json
from .ColorString import ColorString as CorlStr
from .Log import Warn,Info,Error
from .NewId import NewId
from .Obj.UserObj import UserObj

BASIC_RIGHT = ['visitor'] # 처음접속시 기본적으로 지급하는 역할
CLIENTS = {} # 현재 접속해있는 클라이언트 목록
USERS = {} # 저장된 유저 데이터. 데이터베이스와 주기적으로 동기화됨 
NICKNAMES = []



class Server():
    def __init__(self):
        self.addr = None
        self.handlers = {}


    def _isSysMsg(self,msg):
        return (len(msg) > 5) and msg[0:5] == 'wing:'
        
    def _SysMsgEdit(self,msg):
        return msg[5:]

    def _newUser(self,nick,pw):
        id = NewId()
        USERS[id] = UserObj(nick,pw)
        NICKNAMES.append(nick)
        Info(f'새로운 유저: {CorlStr('NEW!',(241, 222, 50))} {CorlStr(nick,(54, 155, 255))}')
        return id

    async def handler(self,websc):
        global USERS,CLIENTS,NICKNAMES
        obj = ClientObj(websc)
        self.address = obj.addressGet() 
        self.clientIP = self.address[0] # ip

        # Info(f"접속: {self.clientIP}")
        async for data in websc:  
            msgLoads = json.loads(data)
            CODE = msgLoads['code']
            DATA = msgLoads['data']
            if self._isSysMsg(CODE):
                CODE = self._SysMsgEdit(CODE)
                
                if CODE == 'signup':
                    NICKNAME = DATA['nickname']
                    PASSWORD = DATA['password']
                    if NICKNAME in NICKNAMES:
                        await obj.send(code='wing:signup',data={'state':'repeatNickname','signup':False})
                        continue
                    if len(PASSWORD) < 4:
                        await obj.send(code='wing:signup',data={'state':'shortPassword','signup':False})
                        continue
                    
                    self._newUser(NICKNAME,PASSWORD)
                
                    await obj.send(code='wing:signup',data={'state':'sueccess','signup':True,'nickname':NICKNAME})

                if CODE == 'login':
                    NICKNAME = DATA['nickname']
                    PASSWORD = DATA['password']
                    if NICKNAME in NICKNAMES:
                        Info(f'유저 로그인: {CorlStr(NICKNAME,((54, 155, 255)))}')
                        await obj.send(code='wing:login',data={'state':'sueccess','login':True,'nickname':NICKNAME})
                    else:
                        await obj.send(code='wing:login',data={'state':'noAccount','login':False})

                await obj._send_()
                continue

            if CODE in list(self.handlers.keys()):
                await self.handlers[CODE](obj,CODE,DATA)

            await obj._send_()
            

        # Info(f'접속종료: {self.clientIP}')


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
                Info(f"{CorlStr('ths wing is open on',(50,255,50))} {CorlStr(f'ws://{addr[0]}:{addr[1]}',(252,70,140))}")
                await asyncio.Event().wait()
                await asyncio.Future()

        try:
            asyncio.run(opener(addr))
        except KeyboardInterrupt:
            Error("키보드 인터럽트 서버 강제종료")

