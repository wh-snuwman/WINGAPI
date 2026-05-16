import wingAPI as wing

ADDR = ('localhost',3000)
client = wing.Client()


@client.main()
async def handler():
    await client.send(code='ping',data={"furit":'apple'})


@client.recv()
async def RECV():
    pass
    

if __name__ == '__main__':
    client.connect(ADDR) 