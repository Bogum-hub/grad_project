import requests

resp = requests.post("http://localhost:5000/pred", files={'file':open('photo/bet.jpg', 'rb')})

print(resp.text)