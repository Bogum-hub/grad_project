import requests

# resp = requests.post("http://127.0.0.1:5000/interaction", files={'file':open('photo/bet.jpg', 'rb')})
# resp = requests.post("http://127.0.0.1:5000/interaction", json={"drugA": '衛署藥製字第032635號', "drugB": '內衛藥製字第001683號'})
# resp = requests.post("http://127.0.0.1:5000/create_schedule", json={"drug": '綠油精', "startDate": '2021-10-10', "endDate": '2021-12-10', "duration": '1', "daily": '12:00:00', "bag": 'c', "hint": '1'})
resp = requests.post("http://127.0.0.1:5000/delete_schedule", json={"sid_list":[5,14]})

print(resp.text)