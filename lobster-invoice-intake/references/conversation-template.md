# Conversation Template

Use this reference to keep the interaction concise and consistent.

## Step 1: show extracted fields

發票 example:

我先辨識到以下內容，請你幫我確認是否正確：
- 發票號碼：AB-12345678
- 品項：文具用品
- 未稅：100
- 稅額：5
- 總額：105
- 收入：
- 餘額：
- 統編：12345678
- 公司名稱：某某有限公司
- 日期：2026-04-07

勞務報酬單 example:

我先辨識到以下內容，請你幫我確認是否正確：
- 發票號碼：未知
- 品項：PT 4hr
- 未稅：500
- 稅額：0
- 總額：500
- 收入：500
- 餘額：
- 統編：未知
- 公司名稱：星夢農場股份有限公司
- 日期：2026-04-05

如果有錯誤或缺漏，直接跟我說要改哪一欄；不知道的欄位可以回我不知道，我會留空。

Rule:
- 勞務報酬單也必須沿用同一組 ledger 欄位格式。
- 不要改成回覆姓名、身分證字號、聯絡電話、地址等原始表單欄位，除非使用者明確要求看原始 OCR。
- 若需要辨識原始表單欄位，也只能作為內部映射依據，對使用者仍優先展示 ledger 欄位結果。

## Step 2: ask only for missing fields

Example:

目前還缺這幾個欄位：
- 發票號碼
- 統編
- 收入
- 餘額

請直接回覆這幾欄的值；如果不知道，就回不知道。

Rule:
- 如果使用者已經在同一則訊息或前一則補上欄位，例如日期、來源、公司名稱、品項、金額，就直接沿用，不要重問。

## Step 3: ask for category

發票 example:

這張發票屬於哪一類？
- 三聯（手開）進項發票
- 電子（傳統）發票進項發票
- 有稅進項發票
- 其他

勞務報酬單 example:

這張單據我建議歸類為「其他」，你要沿用這個類別嗎？

## Step 4: ask for source

Example:

來源是哪裡？如果不清楚也可以直接回不知道。

Rule:
- 如果使用者已經提供來源，就不要再問一次。

## Step 5: final pre-write summary

Example:

我整理後準備寫入以下資料：
- 發票號碼：AB-12345678
- 日期：2026-04-07
- 公司名稱：某某有限公司
- 統編：12345678
- 品項：文具用品
- 未稅：100
- 稅額：5
- 總額：105
- 收入：
- 餘額：
- 類別：有稅進項發票
- 來源：台北門市

如果沒問題，我就寫入 Google Sheet 並上傳圖片。

## Style rules

- Keep replies short.
- Ask only for what is missing.
- Reuse user-supplied ledger fields whenever available.
- Do not dump raw OCR text unless the user asks.
- For 勞務報酬單, do not switch to a non-ledger response format.
- Before sending the extraction reply, quickly verify that every displayed field belongs to the ledger schema.
- If confidence is low, say which ledger field is uncertain.
- If the user says `不知道`, stop asking for that field and leave it blank.
