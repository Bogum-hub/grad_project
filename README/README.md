

## API
* 使用者登入、資料更新
* 藥品辨識
* 藥品查詢
* 用藥時程表
* 交互作用查詢

## TOOL
#### FLASK
#### MYSQL

## CHECK BOX 11/16
- [ ] {['day':'藥袋A、藥袋B']}
- [ ] 過敏array

## Route說明
#### 編輯用藥時程：
route-/create_schedule, request method-PUT
DATA needed: json={"sid", "drug", "startDate", "endDate", "duration", "daily", "bag", "hint"}

#### 取得會員資料：
route-/member_data, request method-GET (在已登入的情況下)
回傳：account, mid, password, name

#### 更新會員資料：
route-/member_update, request method-POST (在已登入的情況下)
DATA needed: json={"name", "password"}

#### 藥品提示搜尋：
route-/search, request method-POST
DATA needed: json={"drug"}
回傳：至多10筆 LIKE drug%(英文) OR %drug%(中文)的結果

#### 查詢用藥時程(for月份)
route-/search_schedule_mon, request method-POST
DATA needed: json={"date", "mon"}
***請注意：date請給年份月份，如2022年12月，則為{"date":"202212", "mon":12} (date為string, mon為integer)
***藥袋起始日期必須相同，功能才正常

#### 新增過敏資訊(在register裡面)
route-/register, request method-POST
DATA needed: json={"username", "account", "password", "allergy"(optional)}
***allergy可填可不填，若為空白，則回傳"username", "account", "password"三者即可(也不需回傳空字串/NA等資訊...)