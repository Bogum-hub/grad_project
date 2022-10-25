import requests

resp = requests.post("http://127.0.0.1:5000/pred", files={'file':open('photo/bet.jpg', 'rb')})
print(resp.text)