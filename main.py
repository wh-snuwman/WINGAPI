import wingAPI as wp
from wingAPI.Server import CorlStr

ADDR = ('localhost',33027)
server = wp.Server()


@server.recv('ping')
async def ping(obj:wp.ClientObj,code:str, data: dict):
    wp.Log.Info(CorlStr(f"{code,data}",(255,255,0)))
    await obj.send(200,{"msg":'pong'})

    await server.broadcastUser(server.allUser(),)


@server.core()
async def core_func():
    await server.sleep(0.2)
    print('hello python!')
    print('hello wingAPI!')

    print(server.rightFilterUser('ingame'))


if __name__ == '__main__':
    server.open(ADDR)
    Lock = server.getLock()