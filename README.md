

## API
* 使用者登入、資料更新
* 藥品辨識
* 藥品查詢
* 用藥時程表
* 交互作用查詢

## TOOL
#### FLASK
#### MYSQL

## CHECK BOX 11/09
- [x] 編輯用藥時程
- [X] 查詢用藥 enddate/start_date
- [x] 取得會員資料的route
- [x] 藥品照片
- [x] 會員資料更新
- [*] 搜尋藥品

## Route說明
#### 編輯用藥時程：
route-/create_schedule, request method-PUT
DATA needed: json={"sid", "drug", "startDate", "endDate", "duration", "daily", "bag", "hint"}

#### 取得會員資料：
route-/member_data/(id), request method-GET
回傳：account, mid, password, name

#### 更新會員資料：
route-/member_update, request method-POST
DATA needed: json={"name", "password"}

#### 藥品提示搜尋：
route-/search, request method-POST
DATA needed: json={"drug"}
備註：目前是回傳10筆 LIKE %drug% 的結果，可進一步討論