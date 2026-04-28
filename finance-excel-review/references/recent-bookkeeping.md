# Recent Bookkeeping Reference

近期帳整理流程的標準參考。用於定義資料蒐集格式、欄位正規化、對照規則與輸出模板。

## 模板基準

使用者已確認：

- `example` 指的就是 `example4_edited by GinnyWu_20260112.xlsx`
- 先依目前下載到的範例檔做初版規格
- 後續有新資料時再迭代調整

## 目標

將近期交易資料整理成兩份 ASCII plain text table：

1. 高信心記帳表，可直接貼上到財務報表
2. 待確認清單，保留人工判斷空間

## 資料來源分層

### 主帳源

用來確認เงินจริง是否已支出或入帳，作為記帳主依據：

- Chase Sapphire Reserve
- American Express
- 中信卡
- 中信帳戶

### 輔助佐證源

用來補充交易內容與分類線索，不單獨作為最終記帳主依據：

- Line Pay
- 街口支付
- 載具
- 電商訂單（蝦皮、momo、PChome 等）

## 建議資料蒐集順序

1. 先收集主帳源資料
2. 再收集輔助佐證源資料
3. 最後統一正規化後再比對

優先接受的輸入形式：

1. CSV / Excel 匯出檔
2. 可複製的交易明細文字
3. 少量補充截圖

若同時有多種格式，優先使用 CSV / Excel，文字作補充，截圖只用於查漏補缺。

## 參考模板來源

使用者提供的 Google Drive 範例資料夾已下載到 workspace：

- `/home/che-an-wu/.openclaw/workspace/data/financial-templates/財務報表範例/Chase Sapphire Reserve 消費記錄.CSV`
- `/home/che-an-wu/.openclaw/workspace/data/financial-templates/財務報表範例/中信卡12月帳單明細查詢_20241219230032.csv`
- `/home/che-an-wu/.openclaw/workspace/data/financial-templates/財務報表範例/中信卡未出帳單明細_20250628.csv`
- `/home/che-an-wu/.openclaw/workspace/data/financial-templates/財務報表範例/中信帳戶12-6月活存明細查詢.xlsx`
- `/home/che-an-wu/.openclaw/workspace/data/financial-templates/財務報表範例/example4_edited by GinnyWu_20260112.xlsx`

若實際讀取到的欄位名稱與本文件不同，以「欄位語意」為準做映射，不要求名稱完全一致。

## 標準欄位 schema

所有來源都先轉成以下統一欄位：

- `source`：來源系統，例如 `chase`、`amex`、`ctbc_card`、`ctbc_bank`、`line_pay`
- `account`：帳戶或卡別名稱，例如 `Chase Sapphire Reserve`
- `tx_date`：交易日
- `post_date`：入帳日或請款日，若無則留空
- `amount`：金額，支出通常記為正數以便後續輸出
- `direction`：`expense` / `income` / `transfer` / `unknown`
- `merchant`：商家或交易對象
- `raw_description`：原始描述
- `payment_channel`：付款管道，例如 `credit_card`、`bank_transfer`、`line_pay`
- `order_id`：訂單編號，若無則留空
- `invoice_id`：發票號碼，若無則留空
- `category_hint`：分類建議，若無法判定則留空
- `note`：補充資訊

## 各來源建議映射

### Chase Sapphire Reserve

實際範例檔：

- `/home/che-an-wu/.openclaw/workspace/data/financial-templates/財務報表範例/Chase Sapphire Reserve 消費記錄.CSV`

實際欄位為：

- `Transaction Date`
- `Post Date`
- `Description`
- `Category`
- `Type`
- `Amount`
- `Memo`

依使用者指定規則，Chase 匯入時採以下映射，且 **example 中的格式不能跑掉**：

- `Description` 複製到目標表的項目描述欄位
- `Amount` 乘以 `-1` 後，作為最終輸出金額
- `Category` 複製到品項 / 分類來源欄位
- `Transaction Date` 只取「日」後複製到日期欄位

正規化建議：

- `source = chase`
- `account = Chase Sapphire Reserve`
- `payment_channel = credit_card`
- `merchant = Description`
- `raw_description = Description`
- `tx_date = Transaction Date`
- `post_date = Post Date`
- `category_hint = Category`

注意：

- Chase 原始 `Amount` 在範例中支出為負數，輸出到記帳表時以 `Amount * -1` 轉成正值
- `Type` 與 `Memo` 可先保留在正規化資料中，必要時寫入 `note`
- 產出最終表時，欄位名稱與順序要對齊 example，不可自行改格式

### American Express

常見可用欄位語意：

- Date → `tx_date`
- Description → `merchant` + `raw_description`
- Amount → `amount`

固定值建議：

- `source = amex`
- `account = American Express`
- `payment_channel = credit_card`

### 中信卡

實際範例檔：

- `/home/che-an-wu/.openclaw/workspace/data/financial-templates/財務報表範例/中信卡12月帳單明細查詢_20241219230032.csv`
- `/home/che-an-wu/.openclaw/workspace/data/financial-templates/財務報表範例/中信卡未出帳單明細_20250628.csv`

目前已確認有兩種格式。

#### 格式 A，帳單明細查詢

實際欄位為：

- `消費日`
- `入帳起息日`
- `摘要`
- `幣別`
- `消費地金額`
- `外幣折算日`
- `消費地`
- `末四碼`
- `新臺幣金額`

映射建議：

- `tx_date = 消費日`
- `post_date = 入帳起息日`
- `merchant = 摘要`
- `raw_description = 摘要`
- `amount = 新臺幣金額`
- `account = 中信信用卡末四碼 + 末四碼`
- `source = ctbc_card`
- `payment_channel = credit_card`

#### 格式 B，未出帳單明細

實際欄位為：

- `交易序號`
- `消費日`
- `入帳日`
- `摘要`
- `卡號末四碼`
- `新臺幣金額`

映射建議：

- `tx_date = 消費日`
- `post_date = 入帳日`
- `merchant = 摘要`
- `raw_description = 摘要`
- `amount = 新臺幣金額`
- `account = 中信信用卡末四碼 + 卡號末四碼`
- `source = ctbc_card`
- `payment_channel = credit_card`

需注意：

- 帳單明細與未出帳明細格式不同，但都映射到相同 schema
- 若 `新臺幣金額` 為負數，例如 `網銀行動繳`，優先視為繳款或轉帳，不直接當消費
- `摘要` 常已帶商家或支付工具線索，例如 `街口電支`、`eTag臨停`、`樂購蝦皮`，可直接作為分類與對照提示

### 中信帳戶

實際範例檔：

- `/home/che-an-wu/.openclaw/workspace/data/financial-templates/財務報表範例/中信帳戶12-6月活存明細查詢.xlsx`

目前已確認主要表頭為：

- `日期`
- `摘要`
- `支出`
- `存入`
- `結餘`
- `備註`
- `對方帳號`
- `註記`

依使用者指定規則，中信帳戶資料匯入時採以下映射，且 **example3 中的格式不能跑掉**：

- `註記` 複製到 `註記`
- `日期` 只取「日」複製到 `消費日`
- `摘要` 複製到 `摘要`
- `備註` 複製到 `備註`
- `支出 / 存入` 的資訊同時用來產生 `美金大概金額` 與 `新台幣金額`

其中金額欄位規則如下：

- `XXX` 代表支出金額，或依使用者指定需要當成負值的存入金額
- `美金大概金額` 的格式為 Excel 公式：`=ROUND(XXX/30,2)`
- `新台幣金額` 的格式為：`XXXNTD XXX/30=YYY` 或依 example3 的空白格式精準輸出
- `YYY` 為 `XXX/30` 的結果

正規化建議：

- `source = ctbc_bank`
- `account = 中信帳戶`
- `payment_channel = bank_account`
- `tx_date = 日期`
- `merchant = 摘要`
- `raw_description = 摘要`
- `note` 可合併 `備註`、`對方帳號`、`註記`

需注意：

- 真實範例中常見 `跨行轉`、`轉帳提`、`手續費`、`現金提` 等摘要，很多不是一般消費，要優先判斷是否列入待確認或 transfer
- 若為存入但實際要求是「負的存入」，依使用者規則保留負號後再進公式與字串格式
- `example4_edited by GinnyWu_20260112.xlsx` 中可見實際輸出示例，例如：
  - 金額欄：`=ROUND((26250+15)/30,2)`
  - 備註欄：`26250+15NTD (26250+15)/30=875.50`
  這代表最終產出時要保留 Excel 公式字串與備註算式字串，不可只填數值

### Line Pay

建議保留：

- 交易日 → `tx_date`
- 商家名稱 → `merchant`
- 金額 → `amount`
- 綁定付款方式 → `note`

固定值建議：

- `source = line_pay`
- `account = Line Pay`
- `payment_channel = line_pay`

### 街口支付

建議保留：

- 交易日 → `tx_date`
- 商家名稱 → `merchant`
- 金額 → `amount`
- 扣款方式 / 帳戶來源 → `note`

固定值建議：

- `source = jkopay`
- `account = 街口支付`
- `payment_channel = jkopay`

### 載具

建議保留：

- 發票日期 → `tx_date`
- 開立商家 → `merchant`
- 金額 → `amount`
- 發票號碼 → `invoice_id`

固定值建議：

- `source = invoice_carrier`
- `account = 載具`
- `payment_channel = invoice`

### 電商訂單

建議保留：

- 下單日 / 完成日 → `tx_date`
- 訂單名稱 / 賣家 / 平台 → `merchant`
- 金額 → `amount`
- 訂單編號 → `order_id`

固定值建議：

- `source = ecommerce`
- `payment_channel = ecommerce`

平台名稱寫入 `account`，例如：

- `account = 蝦皮`
- `account = momo`
- `account = PChome`

## 正規化規則

1. 日期統一轉成 ISO 格式或至少可明確比對年月日
2. 金額去除貨幣符號、逗號與括號，保留純數值
3. 支出統一整理成正數，方向另外記在 `direction`
4. 商家名稱保留原文，同時可建立清理版作為比對用
5. 原始資料中的多餘欄位不進最終表，但可留在 `note`

## 比對規則

以主帳源為核心，一筆主交易去找可能對應的輔助佐證源。

至少符合以下條件才可列為「可能同筆」：

- 金額相同
- 日期接近，預設 ±3 天

再用以下條件提高信心：

- 商家名稱相似
- 平台名稱或支付鏈合理
- 載具 / 電商 / Line Pay / 街口提供一致線索

### 高信心

符合：

- 金額相同
- 日期接近
- 且至少一個額外佐證成立

可放入高信心記帳表。

### 待確認

以下任一情況列入待確認：

- 只有主帳源，找不到任何佐證
- 金額相同但商家完全不清楚
- 同金額候選太多
- 疑似轉帳、退款、信用卡繳款
- 分類無法合理推定

## 欄位填寫規則

### 項目

優先順序：

1. 電商訂單或載具中更清楚的商家 / 訂單名稱
2. Line Pay / 街口的商家名稱
3. 主帳源商家名稱
4. 若仍不清楚，填 `未確認商家`

### 金額

一律以主帳源金額為準。

### 分類

先提供建議分類，常見規則例如：

- 餐廳 / 超商 / 外送 → 餐飲
- 高鐵 / Uber / 停車 / 油資 → 交通
- 蝦皮生活用品 / 家用品 → 日用
- 軟體訂閱 / App / SaaS → 軟體服務
- 銀行手續費 → 金融費用

無法合理判定時，填 `待分類`。

### 方式

盡量寫出支付工具與底層來源，例如：

- `Chase Sapphire Reserve`
- `American Express`
- `中信卡`
- `中信帳戶`
- `Line Pay（綁中信卡）`
- `街口支付（綁中信帳戶）`

### 日

優先使用實際交易日 `tx_date` 的日，不足時再使用 `post_date`，並在備註說明。

### 備註

保留對照與來源資訊，例如：

- `中信卡 + 載具已對應`
- `蝦皮訂單 + 載具已對應`
- `Line Pay 綁中信卡`
- `僅找到卡片扣款，未找到其他佐證`
- `疑似轉帳，待確認`

## 初版來源對模板 mapping

以下 mapping 以 `example4_edited by GinnyWu_20260112.xlsx` 為輸出目標基準，先求可用，再逐步微調。

### 目標工作表觀察

目前可見至少兩種目標表：

#### A. 整理中工作表

例如：`🔒2025_3月同名稱金額合併`

主要欄位：

- `項次`
- `項目`
- `金額`
- `備註`
- `日`
- `分類`
- `方式`
- `v8項目`
- `g原始檔項目`
- `v8分類`
- `g原始分類`
- `v8日`
- `v8金額`
- `g原始檔金額`
- `推測名稱(無更改)`
- `推測分類`

#### B. 完成版工作表

例如：`2025_3月done`

主要欄位：

- `項次`
- `項目`
- `金額`
- `分類`
- `方式`
- `日`
- `備註`
- `推測名稱(無更改)`
- `推測分類`

### Chase 初版 mapping

輸出到整理中工作表時：

- `項目`：先直接用 `Description`
- `金額`：`Amount * -1`
- `備註`：預設空白
- `日`：`Transaction Date` 只取日
- `分類`：先直接沿用人工或規則推測分類；若尚未建立分類表，可先留空或用 `Category` 對照到粗分類
- `方式`：固定填 `chase`
- `v8項目`：可先與 `項目` 相同
- `g原始檔項目`：`Description`
- `v8分類`：目前推測分類
- `g原始分類`：`Category`
- `v8日`：日
- `v8金額`：`Amount * -1`
- `g原始檔金額`：`Amount * -1`

補充規則：

- 若同日、同名稱或可合理合併的多筆交易需要合併，金額欄可保留 Excel 公式字串，例如 `=76.13+ 34.58 `
- `項目` 之後可再透過人工維護的名稱映射表修正，例如 `COUPANG TAIWAN CO. LTD` → `酷澎台灣官網Coupang`
- `Category` 到最終 `分類` 的對照目前先做初版推測，例如：
  - `Food & Drink` → `食`
  - `Groceries` → `食`
  - `Travel` → `行`
  - `Automotive` → `行`
  - `Shopping` → `奢`
  - `Personal` → `其他`
  - 其餘未知 → `其他`

### 中信卡初版 mapping

輸出方向先比照 example4 done 工作表中的呈現方式。

- `項目`：優先用 `摘要` 清理後的商家名稱
- `金額`：初版採 Excel 公式字串 `=ROUND(新臺幣金額/30,2)`
- `分類`：依 `摘要` 做初步分類推測
- `方式`：固定填 `中信信用卡`
- `日`：`消費日` 只取日
- `備註`：`新臺幣金額NTD 新臺幣金額/30=YYY`

摘要清理初版規則：

- 移除尾端城市與國碼資訊，例如 `TAIPEI TW`
- 保留有辨識力的商家名稱，例如：
  - `全聯－文山羅斯福` → `全聯`
  - `樂購蝦皮－katyta...` → `蝦皮` 或 `樂購蝦皮`
  - `街口電支－統一超商` → `街口支付－統一超商`
  - `eTag臨停 EBJ-6273` → `停車費`
- 若為 `網銀行動繳`、卡費扣款或明顯非消費，先列待確認，不直接當一般消費

中信卡分類推測初版：

- `全聯`、超商、餐飲 → `食`
- `eTag`、停車、交通 → `行`
- 電信、App、服務費 → `其他`
- 電商購物 → `奢`
- 無法判斷 → `其他`

### 中信帳戶初版 mapping

以 example4 done 工作表已出現的格式為準。

- `項目`：優先用 `註記`，若無則退回 `摘要`
- `金額`：Excel 公式字串 `=ROUND(XXX/30,2)`，若由多筆組成則用括號與加總，例如 `=ROUND((26250+15)/30,2)`
- `分類`：先留空或依項目推測
- `方式`：固定填 `中信活存`
- `日`：`日期` 只取日
- `備註`：`XXXNTD XXX/30=YYY`

初版判斷規則：

- `摘要` 為 `手續費` 時，優先與前一筆相關交易合併
- `跨行轉`、`轉帳提`、`現金提` 等需要看 `註記` 與 `備註` 補語意
- 若 `註記` 已有明確用途，例如 `每月借款利息`、`洗車美容`，優先拿來當 `項目`
- 若明顯只是資金搬移或難判斷是否屬個人消費，先列待確認

### American Express 初版 mapping

目前尚未拿到實際範例檔，先比照 Chase 處理：

- `項目`：Description 類欄位
- `金額`：支出轉為正值
- `分類`：依來源分類欄位推測到粗分類
- `方式`：固定填 `amex`
- `日`：交易日只取日
- `備註`：預設空白，必要時保留原始描述

### 輔助佐證源初版用途

- `Line Pay`、`街口支付`：主要拿來修正 `項目` 與 `方式`
- `載具`：主要拿來確認商家與金額
- `電商訂單`：主要拿來確認實際購買內容與訂單來源

原則：

- 主帳源決定是否存在該筆帳
- 輔助佐證源幫忙把名稱、分類、方式修到更像 example4 的最終成品

## 輸出模板

### 高信心記帳表

```text
+--------------+----------------------+----------+----------+-----+--------------------------------+
| 項目         | 金額                 | 分類     | 方式     | 日  | 備註                           |
+--------------+----------------------+----------+----------+-----+--------------------------------+
| 全聯         | =ROUND(333/30,2)     | 食       | 中信信用卡 | 1 | 333NTD 333/30=11.10            |
+--------------+----------------------+----------+----------+-----+--------------------------------+
| 借款利息     | =ROUND((26250+15)/30,2) |        | 中信活存 | 1 | 26250+15NTD (26250+15)/30=875.50 |
+--------------+----------------------+----------+----------+-----+--------------------------------+
```

### 待確認清單

```text
+--------------+--------+----------+------------+-----+--------------------------------+
| 項目         | 金額   | 分類     | 方式       | 日  | 備註                           |
+--------------+--------+----------+------------+-----+--------------------------------+
| 網銀行動繳   | 14795  | 待確認   | 中信信用卡 | 12  | 疑似繳卡費或轉帳，不列一般消費 |
+--------------+--------+----------+------------+-----+--------------------------------+
| 跨行轉       | 1437   | 待確認   | 中信活存   | 26  | 需確認是否屬一般支出           |
+--------------+--------+----------+------------+-----+--------------------------------+
```

## 轉換腳本

初版半自動處理器：

- `/home/che-an-wu/.openclaw/workspace/skills/finance-excel-review/scripts/recent_bookkeeping_transform.py`

用途：

- 讀取範例資料夾中的 Chase / 中信卡 / 中信帳戶檔案
- 產出標準化資料與 example4 風格初版資料

使用方式：

```bash
python3 /home/che-an-wu/.openclaw/workspace/skills/finance-excel-review/scripts/recent_bookkeeping_transform.py \
  --input-dir '/home/che-an-wu/.openclaw/workspace/data/financial-templates/財務報表範例' \
  --output-dir '/home/che-an-wu/.openclaw/workspace/data/financial-templates/output' \
  --year 2025 --month 6
```

`--year` 與 `--month` 可省略，不帶時代表全資料；帶入後會先做月份過濾。

目前輸出：

- `normalized_rows.csv`：統一 schema 的原始整理結果
- `example4_rows.csv`：example4 風格的逐筆初版轉換結果
- `example4_grouped_rows.csv`：加入同來源、同方式、同日、同名稱、同分類的合併結果
- `summary.json`：筆數與來源摘要

目前限制：

- 尚未直接寫回 Excel
- 尚未做跨來源去重與對帳合併
- 目前的合併僅限於同來源、同方式、同日、同名稱、同分類
- Amex 尚未接入，因為還沒有實際範例檔
- 名稱清洗與分類仍是初版 heuristic，後續需持續調整

## Agent 執行要求

1. 先問期間，再問可提供哪些來源
2. 先收主帳源，再收輔助佐證源
3. 先正規化欄位，再開始比對
4. 不要直接把原始資料逐筆搬進最終表，必須先經過比對與去重
5. 無法確認時，一律放進待確認清單
6. 除非使用者明確要求，近期帳流程不直接回寫 Excel
