import requests
import json
import random
from Card import Card
from Player import Player
from Pack import Pack

class Draft :

  def __init__(self, id, cubeId, host, channel) :
    self.id = id
    self.cubeId = cubeId
    self.host = host
    self.channel = channel
    self.cards = []
    self.players = {}
    self.numPacks = 3
    self.packSize = 15
    self.setup = False
    self.inProgress = False

  def addParameters(self, numPacks, packSize) :
    self.numPacks = numPacks
    self.packSize = packSize

  def loadCube(self) :
    response = requests.get("http://cubecobra.com/cube/api/cubejson/"+self.cubeId)
    try :
      data = json.loads(response.text)
      for card in data["cards"] :
        self.cards.append(Card(card["cardID"]))
      self.setup = True
      return "Setting up "+self.cubeId+" draft with id "+str(self.id)
    except ValueError as e :
      print(e)
      return "cube not found"

  def maxPlayers(self) :
    return int(len(self.cards)/45)

  def listPlayers(self) :
    text = str(self.getPlayers())+" players have joined draft "+str(self.id)+"\n"
    for i in self.players :
      text += self.players[i].nickname+"\n"
    return text

  def getPlayers(self) :
    return len(self.players)

  def isFull(self) :
    return len(self.players) >= self.maxPlayers()

  def addPlayer(self, username) :
    if self.isFull() :
      return "draft is full"
    if self.inProgress :
      return "draft has already started"
    p = Player(username)
    self.players[str(username)] = p
    return str(p.nickname)+" joins draft "+str(self.id)+", "+str(len(self.players))+"/"+str(self.maxPlayers())+" players have joined"

  def removePlayer(self, username) :
    del self.players[username]

  def hasPlayer(self, username) :
    return username in self.players

  def startDraft(self) :
    if len(self.players) == 0 :
      return "no players in draft"
    if self.inProgress :
      return "draft has already started"  
    self.inProgress = True
    self.loadPacks()
    return "Starting "+str(self.cubeId)+" draft!"

  def loadPacks(self) :
    for name in self.players :
      self.getNewPack(self.players[name])

  def getNewPack(self, player) :
    packList = []
    for i in range(0, self.packSize) :
      packList.append(self.cards.pop(random.randint(0, len(self.cards)-1)))
    pack = Pack(packList)
    player.setPack(pack)

  async def sendPacks(self, callback) :
    for name in self.players :
      await self.players[name].sendPack(callback)

  def getPickName(self, username, pick) :
    player = self.players[username]
    if pick-1 >= player.pack.length() or pick < 1:
      return "invalid pick"
    #card = player.pack.pickCard(pick-1)
    card = player.pack.cards[pick-1]
    #print(player.name+" picks "+card.name)
    #player.addToPool(card)
    return "pick "+card.name+"?"

  def makePick(self, username, pick) :
    player = self.players[username]
    #if pick-1 >= player.pack.length() or pick < 1:
      #return "invalid pick"
    card = player.pack.pickCard(pick-1)
    #print(player.name+" picks "+card.name)
    player.addToPool(card)
    return "picked "+card.name

  async def sendNextPack(self, username, callback) :
    player = self.players[username]
    if player.pack.pick == self.packSize+1 :
      if player.packNum == self.numPacks :
        await self.endDraft(player)
        pass
      else :
        if self.checkReady() :
          await self.sendNewPacks(callback)
        #player.packNum += 1
        #player.pack.pick = 1
        #self.getNewPack(player)
        #await player.sendPack(callback)
    else :
      await self.rotatePacks(player, callback)

  def checkReady(self) :
    for p in self.players :
      print(self.players[p].numPacks())
      if self.players[p].numPacks() > 0 :
        return False
    return True

  async def sendNewPacks(self, callback) :
    for p in self.players :
      p.packNum += 1
      p.pack.pick = 1
      self.getNewPack(p)
      await p.sendPack(callback)

  def getNextPlayer(self, player, increment) :
    if player.name in self.players :
      index = list(self.players).index(player.name)
      keys = list(self.players)
      if index == 0 and increment == -1:
        newPlayer = keys[len(self.players)-1]
      elif index == len(self.players)-1 and increment == 1 :
        newPlayer = keys[0]
      else :
        newPlayer = keys[index+increment]
      return self.players[newPlayer]

  async def rotatePacks(self, player, callback) :
    increment = 1 if player.packNum%2 == 1 else -1
    next = self.getNextPlayer(player, increment)
    print(player.name+" passes to "+next.name)
    pack = player.pack
    text = ""
    index = 1
    for c in player.pack.cards :
      text += " "+str(index)+" "+c.name+"\n"
      index += 1
    print(text)
    if len(player.nextPacks) > 0 :
      print("has next pack")
      player.pack = player.nextPacks.pop(0)
      await player.sendPack(callback)
    else :
      print("no next pack")
      player.pack = None
    next.nextPacks.append(pack)
    if (not next.pack or next.pack.length() == 0) and not next.sending :
      print("next player gets pack")
      next.pack = next.nextPacks.pop(0)
      await next.sendPack(callback)

  async def endDraft(self, player) :
    await player.endDraft()
    for p in self.players :
      if (self.players[p].pick-1) != self.packSize or self.players[p].packNum != self.numPacks :
        return
    await self.resetDraft()

  async def resetDraft(self) :
    await self.channel.send("Draft "+str(self.id)+" ended")
    self.id = -1

  async def viewPool(self, username, callback) :
    player = self.players[username]
    await player.viewPool(callback)

  def getQueue(self) :
    text = ""
    for p in self.players :
      text += self.players[p].nickname+" has "+str(self.players[p].getQueue())+" packs\n"
    return text
    #player = self.players[username]
    #eturn player.getQueue()
