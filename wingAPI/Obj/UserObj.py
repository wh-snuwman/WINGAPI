from ..NewId import NewId

class UserObj():
    def __init__(self,nickname,password,id=None,ClientObj=None):
        self.nickname = nickname
        self.password = password
        self.ClientObj = ClientObj
        self.tag = []
        self.role = 'visitor'
        self.right:set = {}
        self.id = id
        if self.id == None: self.id = NewId()
        self.isLogin = False
        self.isOnline = False

    def giveRight(self,r): self.right.add(r)
    def depriveRight(self,r):self.right.remove(r)
    def setRole(self,r):self.role = r
    def changeIsLogin(self,state):self.isLogin = state

    def getId(self):return self.id
    def getNickname(self):return self.nickname
    def getPassword(self):return self.password
    def getRight(self):return self.right
    def getRole(self):return self.role
    def getTag(self):return self.tag
    def getIsLogin(self):return self.isLogin
    def getConnectClient(self):return self.ClientObj





