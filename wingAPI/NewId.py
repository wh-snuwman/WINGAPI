import secrets,string
CHARACTERS = string.ascii_letters + string.digits
def NewId(length=32):return ''.join(secrets.choice(CHARACTERS) for _ in range(length))
