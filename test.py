import requests

# resp = requests.post("http://127.0.0.1:5000/interaction", files={'file':open('photo/bet.jpg', 'rb')})
resp = requests.post("http://127.0.0.1:5000/interaction", json={"drugA": '衛署藥製字第032632號', "drugB": '內衛藥製字第001683號'})

print(resp.text)