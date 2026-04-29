# Google Sheets & Drive 整合說明

## 兩間公司

| 公司 | Google Sheet 名稱 | Sheet ID |
|------|-------------------|----------|
| 實見 | 實見_2026報帳_openclaw | `1HECA6UydJD3ZJ9td84mF6tvCMWzqzUWKcHHmBwljRGc` |
| 益循 | 益循生活_2026報帳_openclaw | `1OULzT-aiunSfeJOUgZVXY1PI3lmpQ27GAidOHoN_lh8` |

## 欄位結構

### 實見

| 欄位 | B | C | D | E | F | G | H |
|------|---|---|---|---|---|---|---|
| 名稱 | 發票日期 | 姓名 | 公司名稱 | 項目 | 金額 | 有無發票 | 無發票原因 |

### 益循

| 欄位 | B | C | D | E | F | G | H | I |
|------|---|---|---|---|---|---|---|---|
| 名稱 | 發票日期 | 姓名 | 公司名稱 | 開銷單位 | 項目 | 金額 | 有無發票 | 無發票原因 |

**注意：** 益循比實見多了 E 欄「開銷單位」，因此後續欄位（項目、金額等）的位置會往後移一格。

## 資料寫入位置

工作表結構說明：
- 第 1 列：標題列（A1 為「發票上傳」，B1 為 Google Drive 資料夾連結）
- 第 2 列：欄位標題（流水號、發票日期、姓名…）
- 第 3 列起：A 欄已預填流水號（20260301、20260302…），B 欄以後才是資料

寫入步驟：
1. 讀取資料欄範圍：
   - 實見：`gog sheets get <sheetId> "YYYY-MM!B:F" --json`（B 到 F 欄）
   - 益循：`gog sheets get <sheetId> "YYYY-MM!B:G" --json`（B 到 G 欄）
2. 從第 3 列起逐列掃描，找出第一個「所有資料欄位皆為空白」的列號
3. 從該列的 B 欄開始寫入，依據該公司的欄位順序填入

注意事項：
- 嚴禁依流水號推算列號（A 欄預填並不代表該列已有資料）
- 必須以整列資料欄位（實見 B 到 F，益循 B 到 G）是否全部為空白作為判斷依據，任一欄有值即視為非空白列
- 嚴禁自行新增欄位，只允許填寫工作表中既有的欄位

## Google Drive 資料夾（動態讀取）

圖片上傳目標的 Drive 資料夾，從工作表 B1 儲存格動態讀取：

1. 讀取 B1：`gog sheets get <sheetId> "YYYY-MM!B1" --json`
2. B1 值為完整的 Google Drive 連結，如：`https://drive.google.com/drive/folders/<folderId>?usp=drive_link`
3. 萃取資料夾 ID：`/folders/` 後、`?` 前的字串
4. 上傳指令：`gog drive upload <圖片路徑> --name "MMDD $金額_項目.jpg" --parent <folderId> --json`

**嚴禁使用寫死的資料夾 ID，每次都必須從 B1 動態讀取。**

## 日期格式規範

- 寫入 Google Sheet 的日期欄位：`MM/DD/YYYY`（如 `02/18/2026`）
- 圖片檔名中的日期：`MMDD`（如 `0218`）

## 圖片檔名格式

格式：`MMDD $金額_項目.jpg`
範例：`0218 $2099_電費.jpg`

## 工作表名稱格式

格式：`YYYY-MM`（例如 `2026-03`）

## 有無發票欄位值

- 上傳圖片方式報帳：填入「是」
- 手動輸入方式報帳：填入「否」

## 重要操作限制

- 所有 Google Sheet 讀寫操作一律透過 Google Sheets API 直接操作線上檔案
- 嚴禁將檔案下載至本地端後再進行修改
- Google Drive 圖片上傳同樣透過 Drive API 直接上傳
