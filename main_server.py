class SuttaDeck:
    def __init__(self)->None:
        """섯다 전용 덱을 생성합니다. 각 카드는 튜플로 제공되며, 튜플 내 인덱스 0번은 월, 1번은 특수카드 여부입니다. 즉, (1,a)는 1월 특수카드, 1광입니다."""
        self.deck=[]
        for i in range(1,11):
            self.deck.append((i,'a'))
            self.deck.append((i,'b'))
        self.suffle()

    def pop_deck(self, card_num:int=1):
        """덱에서 카드를 뽑습니다. 기본적으로 1장 뽑을때는 기본 카드 형태인 튜플로 제공되나, 복수의 카드를 뽑을 때에는 각 튜플의 리스트 형태로 나갑니다."""
        if card_num==1:
            card_res:tuple = self.deck.pop()
        else :
            card_res:list = []
            for _ in range(card_num):
                card_res.append(self.deck.pop())
        return card_res
    
    def return_deck(self, card:list|tuple)->bool:
        """시용자의 카드를 덱으로 반납합니다. 튜플이나 리스트 둘 다 지원합니다."""
        if str(type(card))=="<class 'list'>":
            self.deck.__iadd__(card)
            return True
        elif str(type(card))=="<class 'tuple'>":
            self.deck.append(card)
            return True
        else : 
            return False
        
    def suffle(self, seed:any=None):
        """덱의 순서를 무작위로 섞습니다."""
        import random
        import time
        if seed==None: 
            random.seed(time.time())
        random.shuffle(self.deck)

class SuttaPlayer:
    def __init__(self, userdata:str=""):
        
        """플레이어 데이터를 불러오거나 새로 생성합니다. userdata에 데이터 값이 있으면 데이터베이스에서 값을 불러들여옵니다.
        시작 금액은 10만원이며, 구성요소는 플레이어의 손패, 보유금, 승수, 패수, 생존여부(게임진행가능여부)입니다."""
        if userdata=="":
            userdata=self.new_userdata()
        get_data = self.get_userdata(userdata)
        self.user:str = get_data[0]
        self.hand:list = []
        self.money:int = get_data[1]
        self.wp:int = get_data[2]
        self.lp:int = get_data[3]
        self.alive = True
        self.called = False
        self.betmoney:int = 0
        if self.money<1000 :
            self.money +=100000

    def get_userdata(self, userdata:str):
        import MySQLdb
        host = '121.173.40.127'
        userid = 'test'
        passwd = 'pswd12#$'
        userdb = 'sesutta'
        con = MySQLdb.connect(host, userid, passwd, userdb)
        cursor = con.cursor()
        query = "SELECT * FROM userdata WHERE usertext=\"%s\""%(userdata)
        cursor.execute(query)
        result = cursor.fetchall()
        print("%s 로그인됨"%result[0][0])
        return result[0]
    
    def new_userdata(self):
        from MySQLdb import _mysql
        import random
        import string
        str_list = string.ascii_letters + string.digits
        randid = random.sample(str_list ,10)
        res:str = ''
        for s in randid: res+=s
        host = '121.173.40.127'
        userid = 'test'
        passwd = 'pswd12#$'
        userdb = 'sesutta'
        con = _mysql.connect(host, userid, passwd, userdb)
        query = "insert into userdata(usertext) values(\"%s\");"%(res)
        con.query(query)
        return res
    
    def get_card(self, card):
        """덱에서 보내온 카드를 손패에 추가합니다. 튜플이나 튜플의 리스트를 지원합니다."""
        if str(type(card))=="<class 'list'>":
            self.hand.__iadd__(card)
            return True
        elif str(type(card))=="<class 'tuple'>":
            self.hand.append(card)
            return True
        return False
    
    def return_card(self):
        """플레이어의 손패에 있는 카드를 덱클래스에 반납합니다."""
        res:list = []
        for h in range(len(self.hand)):
            res.append(self.hand[h])
        self.hand = []
        return res
    
    def win(self, gain_money:int)->None:
        """플레이어가 승리시, 판돈을 회수함과 동시에 승점을 추가합니다."""
        self.wp+=1
        self.money+=gain_money
        self.update_status()
        return
    
    def lose(self):
        """플레이어가 패배시, 패점을 추가합니다."""
        self.lp+=1
        self.update_status()
        return
    
    def update_status(self):
        import MySQLdb
        host = '121.173.40.127'
        userid = 'test'
        passwd = 'pswd12#$'
        userdb = 'sesutta'
        con = MySQLdb.connect(host, userid, passwd, userdb)
        cursor = con.cursor()
        cursor.execute("update sesutta.userdata set money=%d,wp=%d,lp=%d where usertext=\'%s\';"%(self.money,self.wp,self.lp, self.user))
        con.commit()
        con.close()
    
    def lowpanjeong(self)->int:
        """갑오 이하의 승리 우선순위를 결정합니다."""
        if self.hand[0][0]==1 and self.hand[1][0]==2:
            return 17           
        elif self.hand[0][0]==1 and self.hand[1][0]==4:
            return 18
        elif self.hand[0][0]==1 and self.hand[1][0]==9:
            return 19
        elif self.hand[0][0]==1 and self.hand[1][0]==10:
            return 20
        elif self.hand[0][0]==4 and self.hand[1][0]==10:
            return 21
        elif self.hand[0][0]==4 and self.hand[1][0]==6:
            return 22
        else : return 32-((self.hand[0][0]+self.hand[1][0])%10)
    
    def panjeong(self)->int:
        """플레이어에 손패에 맞는 승리 우선순위를 결정합니다. 특수족보인 땡잡이나 암행어사, 재경기는 나중에 처리합니다.
        광땡 및 암행어사 : 0~3, 장땡 : 4, 9땡 ~ 1땡 : 7~15, 땡잡이 6
        멍텅구리구사 : 5, 구사 : 16
        알리 ~ 세륙 : 17 ~ 22
        갑오 ~ 망통 : 23 ~ 32
        """
        #--------------------------------------
        if len(self.hand)<2 : 
            return-1
        self.hand.sort()
        if self.hand[0][0]==4 and self.hand[1][0]==9:
            if self.hand[0][1]==self.hand[1][1]=='a' :
                return 5
            else : 
                return 16 
        elif self.hand[0][1]==self.hand[1][1]=='a' :
            if self.hand[0][0]==3 and self.hand[1][0]==8:
                return 0#38
            elif self.hand[0][0]==1 and self.hand[1][0]==8:
                return 2#18
            elif self.hand[0][0]==1 and self.hand[1][0]==3:
                return 3#13
            elif self.hand[0][0]==4 and self.hand[1][0]==7:
                return 1#47암행, 1끗취급
            elif self.hand[0][0]==3 and self.hand[1][0]==7:
                return 6#37땡잡이, 망통취급
            else : 
                return self.lowpanjeong()
        elif self.hand[0][0]==self.hand[1][0]:
            if self.hand[0][0]==10 : 
                return 4
            else : 
                return 16-self.hand[0][0]
        else : 
            return self.lowpanjeong()
    
    def bet_money(self, bet_money:int)->int:
        """지정된 베팅금액을 판돈에 보탭니다. 보유금 부족시, 보유 가능한 금액을 다 냅니다."""
        if self.alive :
            if self.money<bet_money:
                mtmp = self.money
                self.money=0
                self.betmoney +=int(mtmp)
                return mtmp
            else :
                self.money -= int(bet_money)
                self.betmoney +=int(bet_money)
                return int(bet_money)
        else :
            return 0
    
    def bet_command(self, pandon:int, command:int, defbet:int, lastbet:int)->int:
        """0 : 올인상태 스타터, 1 : 올인상태인 비스타터, 2 : 동의만 얻는 플레이어, 
        3 : 올인이 아닌 스타터, 4 : 올인이 아닌 비스타터"""
        #comList = {0:"다이",1:"콜 or 체크",2:"하프",3:"쿼터",4:"삥"}
        order = None
        print("%s\t보유금%d\n판돈\t낸돈\tpost\t카드"%(self.user,self.money))
        print("%d\t%d\t%d\t"%(pandon, lastbet, self.betmoney),self.hand)
        while type(order)!=int :
            print("0:다이",end='');
            if command==0 or command==3 : 
                print("\t1:체크",end='')
            else : 
                print("\t1:콜",end='')
            if command>2 : 
                print("\t2:하프\t3:쿼터") 
            else :
                print("")
            order = int(input())
            if command<3 :
                if (order<0) or (order>1) :
                    order = "a"
            else :
                if (order<0) or (order>4) :
                    order = "a"
        match order :
            case 0 : self.alive = False; return 0
            case 1 : self.called = True if command!=4 else self.called; return int(lastbet-self.betmoney)
            case 2 : return int(pandon/2)
            case 3 : return int(pandon/4)
            case 4 : return int(defbet)

class Game:
    jokboIndex = {0:"38광땡", 1:"암행어사", 2:"18광땡",3:"13광땡",4:"장땡",5:"멍텅구리구사",
                  6:"땡잡이", 7:"9땡",8:"8땡",9:"7땡",10:"6땡",11:"5땡",12:"4땡",13:"3땡",
                  14:"2땡",15:"1땡",16:"구사",17:"알리",18:"독사",19:"구삥",20:"장삥",
                  21:"장사",22:"세륙",23:"갑오",24:"8끗",25:"7끗",26:"6끗",27:"5끗",
                  28:"4끗",29:"3끗",30:"2끗",31:"1끗",32:"망통"}

    def __init__(self):
        self.player = []
        self.deck = SuttaDeck()
        self.pandon:int = 0
    
    def login_user(self):
        logindata = input("유저데이터 입력. 없을 시 공백 입력")
        self.player.append(SuttaPlayer(logindata))
    
    def Full_Game(self):
        starter = 0
        while (self.Non_Money()) :
            res = self.Set_Game(starter=starter)
            starter=res[0]
            #경기결과 SQL 저장
            print("승자 : %s\t상금 : %d원"%(self.player[starter].user, self.pandon))
            print("이름\t승리\t패배\t보유금\t패")
            for p in self.player:
                if self.player.index(p)==starter: 
                    p.win(self.pandon)
                else : 
                    p.lose()
                print("%s\t%d\t%d\t%d\t"%(p.user, p.wp, p.lp, p.money),end="")
                if len(p.hand)==2 : 
                    print(self.jokboIndex[p.panjeong()] ,p.hand)
                else : 
                    print()
            while True:
                print("커맨드\n0:게임시작\t1:로그인\t2:로그아웃")
                gcom = int(input())
                match gcom:
                    case 0:
                        if len(self.player)>1 : break
                        else : print("인원수가 부족합니다.")
                    case 1:
                        if len(self.player)<6 : self.login_user()
                        else : print("플레이어 수가 너무 많습니다.")
                    case 2: 
                        if len(self.player)>0 : self.logout()
                        else : print("플레이어가 없습니다.")
            if len(self.player)<2 : 
                break
            self.pandon=0
    
    def Set_Game(self, start_money:int=0, defbet:int=1000, starter:int=0):
        """단판 게임을 실행합니다. """
        for p in self.player:
            self.deck.return_deck(p.return_card())
            p.called = False
        self.deck.suffle()
        self.pandon = start_money
        if self.pandon==0:
            for i in range(starter, starter+len(self.player)) :
                s=i
                if s>=len(self.player) : 
                    s-=len(self.player)
                self.player[s].alive=True
                self.pandon+=self.player[s].bet_money(defbet)
            print("1차 베팅")
            self.dispense_card()
            self.bet_all(starter, defbet)
            if self.alive_check()>1:
                print("2차 베팅")
                self.dispense_card()
                self.bet_all(starter, defbet)
        else :
            print("재경기 베팅")
            self.dispense_card(starter=starter,count=2)
            self.bet_all(starter, defbet)
        graderes = self.gradeList()
        if self.alive_check()>1 :
            if (graderes[0][1]==5) or (graderes[0][1]==16) :
                return self.Set_Game(start_money=self.pandon, starter=graderes[0][0])
            if graderes[0][1]==graderes[1][1] :
                for gr in graderes:
                    if gr==graderes[0] : 
                        continue
                    if gr[1]!=graderes[0][1] : 
                        self.player[gr[0]].alive=False
                return self.Set_Game(start_money=self.pandon, starter=graderes[0][0])
        return graderes[0]
       
    def bet_all(self, starter:int=0, dbet:int=1000):
        """현재 생존한 유저들에게서 레이즈를 요청합니다."""
        last:int = 0
        lp:int = -1
        for p in self.player : 
            p.betmoney=0
        for i in range(starter-len(self.player),starter) :
            p:SuttaPlayer = self.player[i]
            if self.alive_check()<2 : 
                break 
            if not p.alive : 
                continue
            elif p.money!=0 :
                if self.player.index(p)==starter:
                    p.bet_money(p.bet_command(self.pandon, 3, dbet, last))
                else :
                    p.bet_money(p.bet_command(self.pandon, 4, dbet, last))
            else :
                if self.player.index(p)==starter:
                    p.bet_money(p.bet_command(self.pandon, 0, dbet, last))
                else :
                    p.bet_money(p.bet_command(self.pandon, 1, dbet, last))
            last = max(last, p.betmoney)
            if p.alive : 
                lp=self.player.index(p)
            self.pandon+=last
        for p in self.player:
            if self.alive_check()<2 : 
                break 
            if p.alive and lp!=self.player.index(p) : 
                self.pandon+=p.bet_money(p.bet_command(self.pandon, 2, dbet, last))
    
    def dispense_card(self, starter:int =0, count:int =1):
        """지정된 매수의 카드를 생존한 각 플레이어에게 지급합니다. 생존한 유저에게만 지급하며, 죽은 유저(다이 선언한 유저)에게는 지급하지 않습니다."""
        for i in range(starter, len(self.player)+starter):
            s = i
            if s>=len(self.player) : 
                s-=len(self.player)
            p:SuttaPlayer = self.player[s]
            if p.alive:
                p.get_card(self.deck.pop_deck(count))
    
    def gradeList(self):
        """각 플레이어에게서 얻은 승리 우선순위를 정렬 후 반환합니다. """
        res = []
        for p in self.player:
            if p.alive : res.append([self.player.index(p), p.panjeong()])
            else : continue
        res.sort(key=(lambda x:x[1]))
        while (res[0][1]==1 and res[1][1]>4)or(res[0][1]==6 and res[1][1]>16):
            p = self.player[res[0][0]]
            res[0][1]=p.lowpanjeong()
            res.sort(key=(lambda x:x[1]))
        return res
    
    def alive_check(self):
        """현재 생존자 수를 반환합니다. 0~5"""
        alres:int = 0
        for p in self.player:
            if p.alive : alres +=1
        return alres
    
    def Non_Money(self):
        """누군가 보유금이 0원이 되면 로그아웃처리 합니다."""
        tmp:bool = True
        for p in self.player:
            if p.money==0:
                self.player.remove(p)
                tmp=False
        return tmp
    
    def logout(self, loid:str=''):
        """userdata값을 받아 로그아웃처리합니다."""
        if loid=='':
            loid=input("로그아웃 아이디? :")
        for p in self.player:
            if p.user==loid:logout = p
            else : continue
        self.player.remove(logout)

if __name__=="__main__":
    g=Game()
    while True :
        print("로그인 유저")
        for l in g.player:
            print(l.user,end="\t")
        print("\n커맨드\n0:게임시작\t1:로그인\t2:로그아웃")
        com = int(input())
        match com:
            case 0:
                if len(g.player)>1 : g.Full_Game()
                else : print("인원수가 부족합니다.")
            case 1:
                if len(g.player)<6 : g.login_user()
                else : print("플레이어 수가 너무 많습니다.")
            case 2: 
                if len(g.player)>0 : g.logout()
                else : print("플레이어가 없습니다.")