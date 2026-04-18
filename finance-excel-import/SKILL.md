---
name: finance-excel-import
description: "Excel 資料匯入助理。將 Slack 上傳的 Excel 檔案資料匯入至指定目標 Excel 檔案的指定工作表，只填入值，不修改任何格式或樣式。Use when: user uploads an Excel file via Slack and wants to import/copy data into another Excel file, or asks to import monthly data into Family Finance Excel."
---

# Finance Excel Import Skill

將 Slack 上傳的來源 Excel 資料填入目標 Excel 工作表。只填入值，禁止修改任何格式。

## 必要工具

所有 Excel 操作**必須使用 excel-xlsx skill**。

---

## 執行前確認資訊

匯入前必須確認以下四項資訊，缺一不可：

| # | 資訊 | 說明 |
|---|---|---|
| 1 | 來源檔案 | 使用者透過 Slack 上傳的 Excel 檔案路徑 |
| 2 | 來源工作表 | 要讀取資料的工作表名稱 |
| 3 | 目標檔案 | 要填入資料的目標 Excel 檔案路徑 |
| 4 | 目標工作表 | 要填入資料的目標工作表名稱 |

若任一資訊缺少，**必須詢問使用者提供**，不得猜測，不得執行匯入。

---

## 匯入工作流程

1. 確認來源檔案（使用者上傳的檔案）
2. 詢問來源工作表
3. 詢問目標檔案
4. 詢問目標工作表
5. 四項資訊確認完整後：
   - 讀取來源工作表資料
   - 將資料填入目標工作表
   - **跳過「項次」欄位，不填寫**
   - **只填入值（value），不帶任何格式**

---

## 匯入規則

### 允許

- 填入資料值（文字、數字）

### 禁止

- 修改目標 Excel 的任何樣式，包括：
  - cell 顏色
  - 字體、字型
  - 欄寬
  - 公式
  - 表格格式

### 項次欄位

**一律跳過，不填寫。**

---

## 行為準則

1. 不自行猜測工作表名稱
2. 不修改 Excel 樣式
3. 不填寫項次欄位
4. 只填入資料值
5. 資訊不足時必須詢問使用者，確認完整後才執行
