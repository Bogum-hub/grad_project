

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
- [ ] 依照輸入的年月分回傳用藥時程表的日期(藥袋不重複)
- [ ] 新增過敏資訊的table


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