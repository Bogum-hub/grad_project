import requests

# resp = requests.post("http://127.0.0.1:5000/interaction", files={'file':open('photo/bet.jpg', 'rb')})
# resp = requests.post("http://127.0.0.1:5000/interaction", json={"drugA": '"培力"維復康膠囊', "drugB": '"海默尼"脊舒S錠10毫克（貝可芬）'})
# resp = requests.post("http://127.0.0.1:5000/create_schedule", json={"drug": '綠油精', "startDate": '2021-10-10', "endDate": '2021-12-10', "duration": '1', "daily": '12:00:00', "bag": 'c', "hint": '1'})
# resp = requests.post("http://127.0.0.1:5000/search_schedule", json={"date":'2021-10-10'})
resp = requests.post("http://127.0.0.1:5000/search_drug", json={"drug":'綠油精'})

print(resp.text)