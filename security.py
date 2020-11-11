import random
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.PublicKey import ECC
from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
import uuid
import keyboard

# 								PROGRAM TAKE SOME TIME TO GENERATE KEYS FOR THE USERS SO GIVE IT AROUND 15 MINUTES

class User:
	def __init__(self, ID, PublicKey, PrivateKey, Coins):
		self.ID = ID
		self.PublicKey = PublicKey
		self.PrivateKey = PrivateKey
		self.Coins = Coins

	def AddCoins(self, C):
		self.Coins = C





class Coin:
	def __init__(self, ID, Signature):
		self.ID = ID
		self.Signature = Signature

	def ChangeSignature(self, Signature):
		self.Signature = Signature



class Transaction:
	def __init__(self, ID, Type, Amount, Sender, Receiver, ListOfCoins, Hash, HashPointer):
		self.ID = ID
		self.Type = Type
		self.Amount = Amount
		self.Sender = Sender
		self.Receiver = Receiver
		self.ListOfCoins = ListOfCoins
		self.Hash = Hash
		self.HashPointer = HashPointer



class Block:
	def __init__(self, ID, List, Hash, HashPointer):
		self.ID = ID
		self.List = List
		self.Hash = Hash
		self.HashPointer = HashPointer



def GetUser(ID):
	global UsersList
	for i in range(len(UsersList)):
		if UsersList[i].ID == ID:
			return UsersList[i]
	return

def MakeCoins(ScroogeKey, Amount):
	CoinsList = []
	for i in range(Amount):
		Co = Coin(str(uuid.uuid1()), None)
		CoinsList.append(SignCoin(Co, ScroogeKey))
	Transaction_ID = str(uuid.uuid1())
	Header = Transaction_ID + str(Amount) + "Scrooge" + "Scrooge"
	Hash = SHA256.new(bytes(Header, 'utf-8'))
	return Transaction(Transaction_ID, "Creating", Amount, "Scrooge", None, CoinsList, Hash, None)


def SendCoins(Amount, Sender, Receiver, ListOfCoins):
	global ListOfTransactions 
	Transaction_ID = str(uuid.uuid1())
	Header = Transaction_ID + str(Amount) + str(Sender) + str(Receiver)
	Hash = SHA256.new(bytes(Header, 'utf-8'))
	T = Transaction(Transaction_ID, "Sending", Amount, Sender, Receiver, ListOfCoins, Hash, None)
	ListOfTransactions.append(T)
	if len(ListOfTransactions) == 10:
		ListOfTransactions = VerifyTransaction(ListOfTransactions)


def VerifyTransaction(LOT):
	global CurrentBlockPointer
	global BlockChain
	global file
	Temp = []
	flag = True
	for i in range(len(LOT)):
		if LOT[i].Type == "Sending":
			SenderUser = GetUser(LOT[i].Sender)
			if flag and LOT[i].Amount <= len(SenderUser.Coins):
				flag = True
			else:
				flag = False

			for j in range(len(LOT[i].ListOfCoins)):
				if flag and VerifyCoin(LOT[i].ListOfCoins[j], SenderUser.PublicKey):
					flag = True
				else:
					flag = False

			if flag:
				for j in range(len(LOT[i].ListOfCoins)):
					f = True
					c = 0
					for z in range(len(LOT)):
						if f:
							c += LOT[z].ListOfCoins.count(LOT[i].ListOfCoins[j])
							if c < 2:
								f = True
							else:
								f = False
					if not f:
						flag = False
			if SenderUser.ID == "Scrooge":
				flag = True
			if flag:
				Temp.append(LOT[i])

		else:
			Temp.append(LOT[i])
	if len(Temp) == 10:
		BlockID = str(uuid.uuid1())
		BlockHash = SHA256.new(bytes(BlockID, 'utf-8'))
		B = Block(BlockID, [], BlockHash, None)
		for i in range(len(Temp)):
			A = AcceptTransaction(Temp[i])
			B.List.append(A)
		if CurrentBlockPointer == "":
			CurrentBlockPointer = B.Hash
			B.HashPointer = None
		else:
			B.HashPointer = CurrentBlockPointer
			CurrentBlockPointer = B.Hash
		BlockChain.append(B)
		pr = "Block_ " + str(B.ID) + "Contains: \n"
		for i in range(len(B.List)):
			pr += "Transaction_ " + B.List[i].ID + ", Transaction type: " + B.List[i].Type + ", Amount of coins: " + str(B.List[i].Amount) + ", Sender: " + str(B.List[i].Sender) + ", Receiver: " + str(B.List[i].Receiver) + ", Hash: " + str(B.List[i].Hash) + ", Previous hash pointer: " + str(B.List[i].HashPointer) + "\n"
		pr += "Block hash: " + str(B.Hash) + ", Block previous pointer: " + str(B.HashPointer) + "\n"
		print(pr)
		print(BlockChain)
		file.write(pr)
		for i in range(len(BlockChain)):
			file.write(str(BlockChain[i]))
		return []
	else:
		return Temp




def AcceptTransaction(T):
	global CurrentPointer
	global UsersList
	if T.Receiver == None:
		if CurrentPointer == "":
			CurrentPointer = T.Hash
			return T
		else:
			T.HashPointer = CurrentPointer
			CurrentPointer = T.Hash
			return T
	else:

		SenderUser = GetUser(T.Sender)
		ReceiverUser = GetUser(T.Receiver)
		SenderUser.Coins = SenderUser.Coins[:len(SenderUser.Coins) - T.Amount]
		for i in range(len(T.ListOfCoins)):
			ReceiverUser.Coins.append(SignCoin(T.ListOfCoins[i], ReceiverUser.PrivateKey))

		T.HashPointer = CurrentPointer
		CurrentPointer = T.Hash
		return T



def SignCoin(C, PK):
	HashID = SHA256.new(bytes(C.ID, 'utf-8'))
	Sign = DSS.new(PK, 'fips-186-3')
	Signature = Sign.sign(HashID)
	C.Signature = Signature
	return C


def VerifyCoin(C, PK):
	verifier = DSS.new(PK, 'fips-186-3')
	h = SHA256.new(bytes(C.ID, 'utf-8'))
	try:
	    verifier.verify(h, C.Signature)
	    return True
	except ValueError:
	    return False


def RandomTransaction():
	global UsersList
	UserSender = random.randrange(23)
	UserReceiver = random.randrange(23)
	RandomAmount = 	int(random.random() * 10)
	if UserSender != 0 and UserReceiver != 0 and UserSender != UserReceiver:
		if (RandomAmount <= len(UsersList[UserSender].Coins)) and RandomAmount > 0:
			SendCoins(RandomAmount, UsersList[UserSender].ID, UsersList[UserReceiver].ID, UsersList[UserSender].Coins[len(UsersList[UserSender].Coins) - RandomAmount:])







def Simulation():
	global file
	global ListOfTransactions
	global BlockChain
	ScroogeKey = DSA.generate(1024)
	UsersList.append(User("Scrooge", ScroogeKey.publickey(), ScroogeKey, []))
	for i in range(25):
		Key = DSA.generate(1024)
		UsersList.append(User(str(uuid.uuid1()), Key.publickey(), Key, []))
	for i in range(len(UsersList)):
		p = "User: " + UsersList[i].ID + ", " + str(UsersList[i].PublicKey) + ", Amount of coins: " + str(len(UsersList[i].Coins)) + "\n"
		print(p)
		file.write(p)
	for i in range(len(UsersList)):
		if i > 0:
			F = MakeCoins(UsersList[0].PrivateKey, 10)
			ListOfTransactions.append(F)
			for z in range(len(F.ListOfCoins)):
				UsersList[0].Coins.append(F.ListOfCoins[z])
			if len(ListOfTransactions) == 10:
				ListOfTransactions = VerifyTransaction(ListOfTransactions)
			SendCoins(10, UsersList[0].ID, UsersList[i].ID, UsersList[0].Coins[len(UsersList[0].Coins) - 10:])

	while True:
		if keyboard.is_pressed('space'):
			Header = str(BlockChain[len(BlockChain)-1].ID)
			HashID = SHA256.new(bytes(Header, 'utf-8'))
			Sign = DSS.new(UsersList[0].PrivateKey, 'fips-186-3')
			Signature = Sign.sign(HashID)
			BlockChain[len(BlockChain)-1].HashPointer = Signature
			p = "\nLast block_ID: " + BlockChain[len(BlockChain)-1].ID + ", Hash of block: " + str(BlockChain[len(BlockChain)-1].Hash) + ", Signature of Scrooge: " + str(BlockChain[len(BlockChain)-1].HashPointer) + "\n"
			print(p)
			file.write(p)
			print("Program Terminated")
			file.close()
			break
		else:
			RandomTransaction()

	


file = open("myfile.txt","w")
ListOfTransactions = []
UsersList = []	
BlockChain = []
CurrentPointer = ""
CurrentBlockPointer = ""
Simulation()

