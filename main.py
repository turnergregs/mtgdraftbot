import discord
import os
import requests
import json
from Draft import Draft
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

admin = "grenrut#9853"

players = {}
setup = False
inProgress = False
host = ""
ogChannel = None
drafts = []

def getFirstOpenDraftId() :
  for draft in drafts :
    if not draft.isFull() :
      return draft
  return None

def getPlayerDraft(username) :
  for draft in drafts :
    if draft.hasPlayer(username) :
      return draft
  return None

def getDraft(command) :
  if len(command) > 1 :
    num = int(command[1])
    for draft in drafts :
      if draft.id == num :
        return drafts[num]
    return None
  else :
    return getFirstOpenDraftId()

def getCardByName(name) :
  return getCard("https://api.scryfall.com/cards/named?fuzzy="+name)

def getCardById(card) :
  return getCard("https://api.scryfall.com/cards/"+card.id, card)

def getCard(url, card = None) :
  response = requests.get(url)
  data = json.loads(response.text)
  if 'image_uris' not in data :
    if 'card_faces' not in data :
      return "card not found"
    else :
      png = ""
      for face in data["card_faces"] :
        png += face["image_uris"]["png"]+"\n"
      if card is not None :
        card.name = data["name"]
        card.png = png
      return png
  if 'png' not in data["image_uris"] :
    return "image not found"
  png = data["image_uris"]["png"]
  if card is not None :
    card.name = data["name"]
    card.png = png
  return png

def getCube(id) :
  return "http://cubecobra.com/cube/list/"+id

def getSamplePack(id) :
  return "http://cubecobra.com/cube/samplepack/"+id

async def startDraft(message, draft) :
  draft.loadPacks()
  await draft.sendPacks(sendFile)

async def sendFile(user, filename, text = "") :
  with open(filename, 'rb') as f:
    picture = discord.File(f)
    channel = await user.create_dm()
    if text != "" :
      await channel.send(text)
    try :
      await channel.send(file=picture)
    except Exception :
      print("error sending pack image")
  os.remove(filename)

async def sendDM(user, text) :
  channel = await user.create_dm()
  await channel.send(text)
  
@client.event
async def on_ready() :
  print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message) :

  command = message.content.split()

  if message.author == client.user :
    return

  elif message.content.startswith('!drafts') :
    if len(drafts) == 0 :
      await message.channel.send("no current drafts")
    else :
      text = ""
      for draft in drafts :
        if draft.id >= 0 :
          text += str(draft.id)+": "+str(draft.cubeId)+", "+str(len(draft.players))+" players\n"
      await message.channel.send(text)

  elif message.content.startswith('!draft') :
    cubeId = command[1]
    draft = Draft(len(drafts), cubeId, str(message.author), message.channel)
    if len(command) == 4 :
      draft.addParameters(int(command[2]), int(command[3]))
    drafts.append(draft)
    await message.channel.send(draft.loadCube())
    if len(draft.cards) == 0 :
      drafts.remove(draft)

  elif message.content.startswith('!join') :
    if len(drafts) == 0 :
      await message.channel.send("no drafts to join")
      return
    username = message.author
    if getPlayerDraft(username) is not None :
      await message.channel.send("you are already in a draft")
      return
    else :
      draft = getDraft(command)
      if draft is None :
        await message.channel.send("all drafts are full")
        return
      elif draft.id < 0 :
        await message.channel.send("draft has already ended")
        return
    await message.channel.send(draft.addPlayer(username))
    if str(username) in draft.players :
      await sendDM(username, "Welcome to the draft!")

  elif message.content.startswith('!leave') :
    username = str(message.author)
    nickname = str(message.author).split("#")[0]
    if len(drafts) == 0 :
      await message.channel.send("no drafts to leave")
    elif len(command) > 1 :
      if drafts[int(command[1])].inProgress :
        await message.channel.send("draft has already started")
      elif username not in drafts[int(command[1])].players :
        await message.channel.send("you aren't in the draft")
      else :
        drafts[int(command[1])].removePlayer(username)
        await message.channel.send(nickname+" has left the draft")
    else :
      draft = getPlayerDraft(username)
      if id is None :
        await message.channel.send("you aren't in any drafts")
      else :
        draft.removePlayer(username)
        await message.channel.send(nickname+" has left the draft")

  elif message.content.startswith('!start') :
    if len(drafts) == 0 :
      await message.channel.send("no draft to start")
    else :
      draft = getDraft(command)
      if draft is None :
        await message.channel.send("draft not found")
      if draft.host != str(message.author) :
        await message.channel.send("only the host can start the draft")
      else :
        await message.channel.send(draft.startDraft())
        if draft.inProgress :
          await startDraft(message, draft)

  elif message.content.startswith('!end') :
    if len(drafts) == 0 :
      await message.channel.send("no drafts to end")
    else :
      draft = getDraft(command)
      if draft is None :
        await message.channel.send("draft not found")
      if draft.host != str(message.author) and str(message.author) != admin :
        await message.channel.send("only the host can end the draft")
      else :
        await message.channel.send("ended draft "+str(draft.id))
        draft.id = -1

  elif message.content.startswith('!pick') :
    if len(drafts) == 0 :
      await message.channel.send("no current draft")
    elif not isinstance(message.channel, discord.channel.DMChannel) :
      await message.channel.send("picks can only be made after a pack is sent")
    elif len(command) == 1 :
      await message.channel.send("please specify which card to pick")
    else :
      username = str(message.author)
      draft = getPlayerDraft(username)
      if draft is None :
        await message.channel.send("you aren't in a draft")
      else :
        text = draft.makePick(username, int(command[1]))
        await message.channel.send(text)
        if text != "invalid pick" :
          await draft.sendNextPack(username, sendFile)


        #text = draft.getPickName(username, int(command[1]))
        #if text != "invalid pick" :
          #msg = await message.channel.send(text)
          #await msg.add_reaction("👍")
          #await msg.add_reaction("👎")

          #def check(reaction, user) :
            #return user == username
          
          #res = await client.wait_for("reaction_add", check=check)
          #if res:
            #reaction, user = res
            #if str(reaction.emoji) == ":+1:":
              #draft.makePick(username, int(command[1]))
              #await draft.sendNextPack(username, sendFile)
            #if str(reaction.emoji) == ":-1:":
              #await message.channel.send("please pick again")
          

  elif message.content.startswith('!pool') :
    if len(drafts) == 0 :
      await message.channel.send("no current drafts")
    else :
      username = str(message.author)
      draft = getPlayerDraft(username)
      if draft is None :
        await message.channel.send("You aren't in a draft")
      else :
        await draft.viewPool(username, sendFile)

  elif message.content.startswith('!players') :
    if len(drafts) == 0 :
      await message.channel.send("no current drafts")
    else :
      draft = getDraft(command)
      if draft is None :
        await message.channel.send("draft doesn't exist")
      #await message.channel.send(str(draft.getPlayers())+" players have joined draft "+str(draft.id))
      await message.channel.send(draft.listPlayers())

  elif message.content.startswith('!queue') :
    if len(drafts) == 0 :
      await message.channel.send("no current drafts")
    #username = command[1]
    #draft = getPlayerDraft(username)
    #if draft is None :
      #await message.channel.send("That player isn't in a draft")
    else :
      draft = getDraft(command)
      if draft is None :
        await message.channel.send("draft doesn't exist")
      elif not draft.inProgress :
        await message.channel.send("draft hasn't started yet")
      await message.channel.send(draft.getQueue())
    
  elif message.content.startswith('!card') :
    text = ""
    for word in command :
      if word != command[0] :
        text += word
    await message.channel.send(getCardByName(text))

  elif message.content.startswith('!cube') :
    await message.channel.send(getCube(command[1]))

  elif message.content.startswith('!pack') :
    await message.channel.send(getSamplePack(command[1]))

  elif message.content.startswith('!help') :
    text =  "!card <cardname> - posts the card image\n"
    text += "!cube <cubecobraid> - links the cube with that id\n"
    text += "!pack <cubecobraid> - posts a sample pack from the cube with that id\n"
    text += "!draft <cubecobraid> - sets up standard draft for cube with that id\n"
    text += "!draft <cubecobraid> <packs> <packsize> - sets up draft with specified number of packs and picks\n"
    text += "!join - joins a draft that is being set up\n"
    text += "!start - starts a draft that is being set up, only the host can start\n"
    text += "!end - ends a draft being run, only the host can end\n"
    text += "!pick <number> - picks the card with the specified number in a pack, can only be made in private chat with bot\n"
    text += "!pool - displays your current draft pool, can only be done in private chat with bot\n"
    text += "!players - lists the usernames of players currently in the draft"
    await message.channel.send(text)

#client.run(os.getenv('TOKEN'))
client.run(TOKEN)