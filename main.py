import whitePaper as wp

ADDR = ('localhost',3000)
client = wp.Client()


@client.main()
async def handler():
    # while True:
    await client.send(code='ping',data={"furit":'apple'})




if __name__ == '__main__':
    client.connect(ADDR)