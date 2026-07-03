import wingAPI as wing
from wingAPI.colorstring import colorString

ADDR = ('localhost',4000)
server = wing.Server()


@server.recv('ping')
async def ping(obj:wing.ClientObj, data: dict):

    server.info(colorString(f"{data}",(255,255,0)))

    await obj.send('pong',{"msg":'pong'})

@server.error()
async def error_func(obj:wing.ClientObj,error):
    pass

@server.end()
async def end_func(obj:wing.ClientObj):
    pass

if __name__ == '__main__':
    server.open(ADDR)
    Lock = server.getLock()