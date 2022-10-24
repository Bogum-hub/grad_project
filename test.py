import requests

resp = requests.post("https://dont-drug-out.herokuapp.com/pred", files={'file':open('photo/bet.jpg', 'rb')})

print(resp.text)