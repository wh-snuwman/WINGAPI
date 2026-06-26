import wingAPI as wp
from wingAPI.Server import CorlStr

ADDR = ('localhost',4000)
server = wp.Server()


@server.recv('ping')
async def ping(obj:wp.ClientObj, data: dict):
    wp.Log.Info(CorlStr(f"{data}",(255,255,0)))
    await obj.send('pong',{"msg":'pong'})

@server.error()
async def error_func(obj:wp.ClientObj,E):
    pass

@server.end()
async def end_func():
    pass

@server.core()
async def core_func():
    pass

if __name__ == '__main__':
    server.open(ADDR)
    Lock = server.getLock()