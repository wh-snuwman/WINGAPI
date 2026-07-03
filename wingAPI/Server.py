from .Log import Warn,Info,Error
import websockets
import asyncio
import json
from .colorstring import colorString as CorlStr
from .NewId import NewId
from .Obj.UserObj import UserObj
from .Obj.ClientObj import ClientObj
from .ReservedWord import RESERVED_WORD
import traceback


USERS = {} # 저장된 유저 데이터. 데이터베이스와 주기적으로 동기화됨 
CLIENTS = {} # 현재 접속해있는 클라이언트 목록


class Server():
    def __init__(self):
        self.addr = None
        self.handlers = {}
        self.core_func = None
        self.error_count = 0 # 에러가 발생한 횟수. 특정 횟수 이상이면 서버 강제 리부팅 

        async def temp(obj:ClientObj): 
            Error(traceback.format_exc())
            self.error_count += 1

        self.end_func = temp
        self.error_func = None
        self.login_func = None
        self.Lock = None


    def getUser(self,infoType='id',info = str) -> UserObj:
        if infoType == 'id':
            return USERS[info]
        elif infoType == 'nick':
            for userObj in list(USERS.values()):
                if userObj.nickname == info: 
                    return userObj
                
        else:
            raise Exception("잘못된 인자값")


    def _getAllUser(self,type='id'):
        if type == 'id':return [i.id for i in list(USERS.values())]
        if type == 'nick':return [i.nickname for i in list(USERS.values())]


    def _isSysMsg(self,msg):
        return (len(msg) > 5) and msg[0:5] == 'wing:'


    def _editSysMsg(self,msg):
        return msg[5:]
    

    def _newUser(self,nick,pw,obj):
        id = f'USER{NewId()}'
        USERS[id] = UserObj(nick,pw,id,obj)
        Info(f'New user: {CorlStr('NEW!',(241, 222, 50))} {CorlStr(nick,(54, 155, 255))}')
        return id


    def _rmClient(self,id):
        if id in list(CLIENTS.keys()):
            del CLIENTS[id]
        else:
            Error('no client')
            self.error_count += 1


    def _addClient(self,websc):
        id = f'CLIENT{NewId()}'
        _obj = ClientObj(websc,id)
        CLIENTS[id] = _obj
        return _obj,id

    
    async def handler(self, websc):
        obj, objId = self._addClient(websc)
        obj: ClientObj
        uobj: UserObj = None
        address = obj.addressGet()
        Info(f'Client Connect | IP: {CorlStr(address[0],(252,70,140))} | ID: {obj.getId()}')
        
        try:
            async for data in websc:  
                msgLoads = json.loads(data)
                CODE = msgLoads[RESERVED_WORD[0]]
                DATA = msgLoads[RESERVED_WORD[1]]

                if self._isSysMsg(CODE):
                    CODE = self._editSysMsg(CODE)
                    if CODE == 'signup':
                        NICKNAME = str(DATA['nickname'])
                        PASSWORD = str(DATA['password'])

                        if NICKNAME in self._getAllUser('nick'):
                            obj.send(code='wing:signup', data={'state':'repeatNickname','signup':False})
                        elif len(PASSWORD) < 4:
                            obj.send(code='wing:signup', data={'state':'shortPassword','signup':False})
                        else:
                            _id = self._newUser(NICKNAME, PASSWORD, obj)
                            obj.connectUser(_id)
                            
                            obj.send(code='wing:signup', data={'state':'sueccess','signup':True,'nickname':NICKNAME})

                    if CODE == 'login':
                        NICKNAME = str(DATA['nickname'])
                        PASSWORD = str(DATA['password'])

                        if NICKNAME in self._getAllUser('nick'):

                            uobj = self.getUser('nick', NICKNAME) 

                            if uobj.getPassword() != PASSWORD:
                                obj.send(code='wing:login', data={'state':'passwordWorng','login':False})
                            else:
                                Info(f'User login: {CorlStr(NICKNAME,((54, 155, 255)))}')

                                uobj.changeIsLogin(True)
                                await self.login_func(obj,self.getUser('nick',NICKNAME))

                                obj.send(code='wing:login', data={'state':'sueccess','login':True,'nickname':NICKNAME})
                        else:
                            obj.send(code='wing:login', data={'state':'noAccount','login':False})

                    await obj._send_()
                    continue
                
                else:
                    if CODE in list(self.handlers.keys()):
                        await self.handlers[CODE](obj, DATA)

                await obj._send_()
                
            await self.end_func(obj)

        except Exception as e:
            Info(f"Client connection is abnormally disconnected | ID: {obj.getId()}")
            await self.error_func(obj,e)
            print(traceback.format_exc())
            self.optimizationClient()



        # finally:
        if uobj and uobj.getIsLogin():
            uobj.changeIsLogin(False)
            Info(f'User Logout: {uobj.nickname}')
            uobj.changeConnectClient(None)
            uobj.ClientObj = None
            uobj.isLogin = False
            uobj.right = []
            uobj.tag = []


        Info(f'client disconnect | IP: {CorlStr(address[0],(252,70,140))} | ID: {obj.getId()}')
        self._rmClient(obj.getId())

    def newlogin(self):
        def decorator(func):
            self.login_func = func
            return func
        return decorator 
    

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
    

    def error(self):
        def decorator(func):
            self.error_func = func
            return func
        return decorator 
    

    def end(self):
        def decorator(func):
            self.end_func = func
            return func
        return decorator 
    

    async def sleep(self,time):
        await asyncio.sleep(time)


    def allUser(self):
        return USERS


    def getLock(self):
        return self.Lock


    def optimizationClient(self): # 서버에 과부하가 걸렸을때 모두 정리
        Warn('Start client optimization')
        arr = []
        for k,v in CLIENTS.items():
            k : str
            v : ClientObj
            if v == None:
                arr.append(k)
        for i in arr:
            del CLIENTS[i]
        Warn('Success client optimization')



    async def broadcastClient(self,code=str,data={}) -> list:
        arr = []
        for _id,obj in CLIENTS.items():
            obj:ClientObj
            obj.send(code,data)
            await obj._send_()
            arr.append(_id)
        return arr


    async def broadcastUser(self,who=list[UserObj],code=str,data={}) -> list[ClientObj]:
        arr = []
        for _uobj in who:
            try:
                _uobj:UserObj
                _obj = _uobj.getConnectClient()
                _obj:ClientObj
                _obj.send(code,data)    
                arr.append(_uobj)
                await _obj._send_()
            except Exception as e:
                if _uobj != None:
                    await self.error_func(_uobj.getConnectClient(),e)
                self.optimizationClient()
                self.error_count += 1
        return arr


    def roleFilterUser(self,role):
        return [uobj for _,uobj in USERS.items() if role in uobj.getRole()]


    def rightFilterUser(self,right):
        return [uobj for _,uobj in USERS.items() if right in uobj.getRight()]


    def tagFilterUser(self,tag):
        return [uobj for _,uobj in USERS.items() if tag in uobj.getTag()]


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
            Error("Hardware interrupt server shutdown")


Info(f'Success Initialization wingAPI')
