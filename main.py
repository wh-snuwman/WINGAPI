import whitePaper as wp
from whitePaper.Server import CorlStr

ADDR = ('localhost',1270)
server = wp.Server()


@server.recv('ping')
async def ping(obj:wp.ClientObj,code:str, data: dict):
    wp.Log.Info(CorlStr(f"{code,data}",(255,255,0)))
    await obj.send(200,{"msg":'pong'})




if __name__ == '__main__':
    server.open(ADDR)