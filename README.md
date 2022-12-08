## API
* 使用者登入、資料更新
* 藥品辨識
* 藥品查詢
* 用藥時程表
* 交互作用查詢

## TOOL
#### FLASK
#### MYSQL

## CHECK BOX 
- [x] null

## Route說明

#### 會員註冊
route-/member_register, request method-POST 
DATA needed: json={"name", "account", "password", "allergy", "bag"}
allery 範例： 'allergy':[{'drug':'綠油精'}, {'drug':'暈速寧片'}]
***allergy可填可不填，若為空白，則回傳"username", "account", "password"三者即可(也不需回傳空字串/NA等資訊...)
bag 範例： 'bag':[{'藥袋A':[{'startDate':'2022-12-08'},{'endDate':'2022-12-09'}]}, {'藥袋B':[{'startDate':'2022-12-08'},{'endDate':'2022-12-10'}]}, {'藥袋C':[{'startDate':'2022-12-08'},{'endDate':'2022-12-11'}]}]
***bag為必填

#### 取得會員資料：
route-/member_data, request method-GET (在已登入的情況下)
回傳：account, mid, password, name, allergy, bag

#### 更新會員資料：
route-/member_update, request method-POST (在已登入的情況下)
DATA needed: json={"name", "account", "password", "allergy", "bag"}

#### 新增用藥時程：
route-/create_schedule, request method-POST
DATA needed: json={"drug", "duration", "daily", "scheduleBagId", "hint"}

#### 編輯用藥時程：
route-/create_schedule, request method-PUT
DATA needed: json={"sid", "drug", "duration", "daily", "scheduleBagId","hint"}

#### 查詢用藥時程(for月份)
route-/search_schedule_mon, request method-POST
DATA needed: json={"date", "mon", "year"}
***請注意：date請給年份月份，如2022年12月，則為{"date":"202212", "mon":12, "year":2022} (date為string, mon&year為integer)

#### GET使用者schedule
route-/search_schedule, request method-GET

#### 藥品提示搜尋：
route-/search, request method-POST
DATA needed: json={"drug"}
回傳：至多10筆 LIKE drug%(英文) OR %drug%(中文)的結果

