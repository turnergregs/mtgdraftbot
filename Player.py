import discord
import os
from Pack import Pack

class Player:
  pick = 1

  def __init__(self, author):
    self.user = author
    self.name = str(author)
    self.nickname = str(author).split("#")[0]
    self.pool = []
    self.pack = []
    self.packNum = 1
    self.nextPacks = []
    self.sending = False

  def setPack(self, pack) :
    self.pack = pack

  async def sendPack(self, callback) :
    print(self.name)
    text = "pack "+str(self.packNum)+" pick "+str(self.pack.pick)
    if self.packNum == 1 and self.pack.pick == 1 :
      text += "\nType !pick followed by the number of the card you want to pick"
    await callback(self.user, self.pack.getPackFile(self.name), text)

  def addToPool(self, card):
    self.pool.append(card)

  async def viewPool(self, callback) :
    temp = Pack(self.pool)
    poolSize = 7
    await callback(self.user, temp.getPackFile(str(self.name)+"pool", poolSize), "Here are the cards you've picked so far")

  def numPacks(self) :
    pack = 1 if self.pack != [] and self.pack is not None else 0
    return pack + len(self.nextPacks)

  def getQueue(self) :
    return self.numPacks()

  async def endDraft(self) :
    filename = "draft"+self.name+".txt"
    file = open(filename, "w")
    for card in self.pool :
      file.write(card.name+"\n")
    file = open(filename, "r")
    channel = await self.user.create_dm()
    await channel.send(file=discord.File(r'draft'+self.name+'.txt'))
    os.remove(filename)