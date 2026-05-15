import whitePaper as wp
from whitePaper.server import colorString

ADDR = ('localhost',3000)
server = wp.Server()
# wp.Warn
wp.Log.Info()

@server.recv('ping')
def test(websc,message:str):
    wp.Server.INFO(colorString(message,(255,255,0)))




if __name__ == '__main__':
    server.open(ADDR)