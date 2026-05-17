from .Log import Warn,Info,Error
Info(f'모듈로드 시작..')
import websockets
import asyncio
import json
from .ColorString import ColorString as CorlStr
from .NewId import NewId
from .Obj.UserObj import UserObj
from .Obj.ClientObj import ClientObj
from .ReservedWord import RESERVED_WORD
Info(f'모든 모듈로드 성공!')

# BASIC_RIGHT = ['visitor'] # 처음접속시 기본적으로 지급하는 역할
USERS = {} # 저장된 유저 데이터. 데이터베이스와 주기적으로 동기화됨 
CLIENTS = {} # 현재 접속해있는 클라이언트 목록

class Server():
    def __init__(self):
        self.addr = None
        self.handlers = {}
        self.core_func = None
        self.Lock = None


    def _getUser(self,infoType='id',info = str):
        if infoType == 'id':
            return USERS[info]
        if infoType == 'nick':
            for userObj in list(USERS.values()):
                if userObj.nickname == info: 
                    return userObj
        raise Exception("잘못된 인자값")


    def _getAllUser(self,type='id'):
        if type == 'id':return [i.id for i in list(USERS.values())]
        if type == 'nick':return [i.nickname for i in list(USERS.values())]


    def _isSysMsg(self,msg):
        return (len(msg) > 5) and msg[0:5] == 'wing:'


    def _editSysMsg(self,msg):
        return msg[5:]
    

    def _newUser(self,nick,pw,obj):
        id = NewId()
        USERS[id] = UserObj(nick,pw,id,obj)
        Info(f'새로운 유저: {CorlStr('NEW!',(241, 222, 50))} {CorlStr(nick,(54, 155, 255))}')
        return id


    def _rmClient(websc,id):
        CLIENTS.pop(id)

    def _addClient(self,websc):
        id = NewId()
        _obj = ClientObj(websc,id)
        CLIENTS[id] = _obj
        return _obj,id

    async def handler(self,websc):
        obj,objId= self._addClient(websc)
        obj : ClientObj
        uobj : UserObj
        address = obj.addressGet()

        Info(f'클라이언트 접속 | IP: {CorlStr(address[0],(252,70,140))} | ID: {obj.getId()}')

        async for data in websc:  
            msgLoads = json.loads(data)
            CODE = msgLoads[RESERVED_WORD[0]]
            DATA = msgLoads[RESERVED_WORD[1]]
            if self._isSysMsg(CODE):
                CODE = self._editSysMsg(CODE)
                if CODE == 'signup':
                    NICKNAME = DATA['nickname']
                    PASSWORD = DATA['password']

                    if NICKNAME in self._getAllUser('nick'):
                        await obj.send(code='wing:signup',data={'state':'repeatNickname','signup':False})
                    elif len(PASSWORD) < 4:
                        await obj.send(code='wing:signup',data={'state':'shortPassword','signup':False})
                    else:
                        id = self._newUser(NICKNAME,PASSWORD,obj)
                        await obj.send(code='wing:signup',data={'state':'sueccess','signup':True,'nickname':NICKNAME})

                if CODE == 'login':
                    NICKNAME = DATA['nickname']
                    PASSWORD = DATA['password']
                    if NICKNAME in self._getAllUser('nick'):
                        uobj = self._getUser('nick',NICKNAME) 

                        if uobj.getPassword() != PASSWORD:
                            await obj.send(code='wing:login',data={'state':'passwordWorng','login':False})
                            
                        else:
                            Info(f'유저 로그인: {CorlStr(NICKNAME,((54, 155, 255)))}')
                            uobj.changeIsLogin(True)
                            await obj.send(code='wing:login',data={'state':'sueccess','login':True,'nickname':NICKNAME})

                    else:
                        await obj.send(code='wing:login',data={'state':'noAccount','login':False})

                await obj._send_()
                continue

            if CODE in list(self.handlers.keys()):
                await self.handlers[CODE](obj,CODE,DATA)
            await obj._send_()
            
        if uobj.getIsLogin():
            uobj.changeIsLogin(False)
            Info(f'유저가 로그아웃했습니다 (접속종료) nickname:{uobj.nickname}')

        Info(f'클라이언트 접속종료 | IP: {CorlStr(address[0],(252,70,140))} | ID: {obj.getId()}')
        self._rmClient(objId)


    def recv(self, _msg=None):
        def decorator(func):
            if _msg != None:
                self.handlers[_msg] = func
            return func
        return decorator
    

    def core(self):
        def decorator(func):
            self.core_func = func
            return func
        return decorator 


    async def sleep(self,time):
        await asyncio.sleep(time)


    def allUser(self):
        return USERS


    def getLock(self):
        return self.Lock

    
    def broadcastClient(self,code=str,data={}) -> list:
        arr = []
        for _id,obj in CLIENTS.items():
            obj:ClientObj
            obj.send(code,data)
            obj._send_()
            arr.append(_id)
        return arr


    def broadcastUser(self,who=dict,code=str,data={}):
        arr = []
        for _id,uobj in who.items():
            uobj:UserObj
            obj = uobj.getConnectClient()
            obj:ClientObj
            obj.send(code,data)
            obj._send_()
            arr.append(_id)
        return arr

    def roleFilterUser(self,role):
        return [uobj for uobj in USERS if role in uobj.getRole()]

    def rightFilterUser(self,right):
        return [uobj for uobj in USERS if right in uobj.getRight()]

    def tagFilterUser(self,tag):
        return [uobj for uobj in USERS if tag in uobj.getTag()]


    def open(self,addr):
        self.addr = addr
        self.Lock = asyncio.Lock()

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

        async def core_opener():
            await self.core_func()

        async def main():
            await asyncio.gather(core_opener(),opener(addr=addr))

        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            Error("키보드 인터럽트 서버 강제종료")



Info(f'wingAPI 초기화 완료')
