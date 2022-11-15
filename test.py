import requests

# resp = requests.post("http://127.0.0.1:5000/pred", files={'file':open('photo/bet.jpg', 'rb')})
# resp = requests.post("http://127.0.0.1:5000/interaction", json={"drugA": '"培力"維復康膠囊', "drugB": '"海默尼"脊舒S錠10毫克（貝可芬）'})
# resp = requests.post("http://127.0.0.1:5000/create_schedule", json={"drug": '綠油精', "startDate": '2021-10-10', "endDate": '2021-12-10', "duration": '1', "daily": '12:00:00', "bag": 'c', "hint": '1'})
# resp = requests.post("http://127.0.0.1:5000/search_schedule", json={"date":'2021-12-01'})
resp = requests.post("http://127.0.0.1:5000/search", json={"drug":'藥布'})
# resp = requests.post("http://127.0.0.1:5000/search_drug", json={"drug":'舒以明片'})
# resp = requests.put("http://127.0.0.1:5000/create_schedule", json={"sid":'18', "drug": '綠油精', "startDate": '2021-10-10', "endDate": '2021-12-10', "duration": '1', "daily": '12:00:00', "bag": '藥袋C', "hint": '1'})
# resp = requests.get("http://127.0.0.1:5000/member_data/11")
# resp = requests.post("http://127.0.0.1:5000/member_update", json={"name":'阿洪', "password":'123456'})

print(resp.text)