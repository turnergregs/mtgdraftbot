import requests
import json

class Card :

  url = "https://api.scryfall.com/cards/"

  def __init__(self, id) :
    self.id = id
    self.url += str(id)

  def getData(self) :
    response = requests.get(self.url)
    data = json.loads(response.text)
    png = ""
    if 'image_uris' not in data :
      if 'card_faces' in data :
        for face in data['card_faces'] :
          png += face['image_uris']['png']+"\n"
    else :
      png = data['image_uris']['png']
    self.png = png
    self.img = requests.get(png, stream=True).raw
    self.name = data['name']
    return self
  