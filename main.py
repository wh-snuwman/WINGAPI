import whitePaper as wp
from whitePaper.Server import CorlStr

ADDR = ('localhost',3000)
server = wp.Server()


@server.recv('ping')
def test(websc,message:str):
    wp.Log.Info(CorlStr(message,(255,255,0)))




if __name__ == '__main__':
    server.open(ADDR)