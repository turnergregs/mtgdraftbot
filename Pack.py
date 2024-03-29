from PIL import Image
import requests
import math

class Pack :

  def __init__(self, pack) :
    self.packSize = len(pack)
    self.pick = 1
    self.cards = self.loadPack(pack)

  def length(self) :
    return len(self.cards)
  
  def loadPack(self, pack) :
    cards = []
    for card in pack :
      cards.append(card.getData())
    return cards

  def pickCard(self, index) :
    self.pick += 1
    return self.cards.pop(index)

  def getPackFile(self, name, width=5) :
    height = math.ceil(len(self.cards)/width)
    imgs = []
    text = ""
    for card in self.cards :
      text += str(card.name)+', '
      imgs.append(requests.get(card.png, stream=True).raw)
    print(text)
    images = [Image.open(x) for x in imgs]
    widths, heights = zip(*(i.size for i in images))
    #total_width = sum(widths)
    total_width = widths[0]*width
    max_height = max(heights)*height
    card_height = heights[0]

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    y_offset = 0
    for im in images:
      new_im.paste(im, (x_offset,y_offset))
      x_offset += im.size[0]
      if (images.index(im)+1)%5 == 0 :
        x_offset = 0
        y_offset += card_height

    filename = 'pack'+name+'.jpg'
    new_im.save(filename)
    return filename