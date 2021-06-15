import discord
import os

class Player:
  pick = 1

  def __init__(self, author):
    self.user = author
    self.name = str(author)
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

  def viewPool(self) :
    text = ""
    for card in self.pool :
      text += card.name+"\n"
    return text

  def getQueue(self) :
    return self.name+" has "+str(len(self.nextPacks))+" packs"

  async def endDraft(self) :
    filename = "draft"+self.name+".txt"
    file = open(filename, "w")
    for card in self.pool :
      file.write(card.name+"\n")
    file = open(filename, "r")
    channel = await self.user.create_dm()
    await channel.send(file=discord.File(r'draft'+self.name+'.txt'))
    os.remove(filename)