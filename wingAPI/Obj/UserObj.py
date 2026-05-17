from ..NewId import NewId

class UserObj():
    def __init__(self,nickname,password):
        self.nickname = nickname
        self.password = password
        self.tag = []
        self.role : str
        self.right : set
        self.id = NewId()
    def nickname_get(self):
        return self.nickname

    def password_get(self):
        return self.password

    def giveRight(self,r):
        self.right.add(r)

    def depriveRight(self,r):
        self.right.remove(r)

    def setRole(self,r):
        self.role = r

    def role_get(self,r):
        self.role = r

    def right_get(self):
        return self.right
