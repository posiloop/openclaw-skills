---
name: lobster-invoice-intake
description: Handle invoice-image intake for the Google Sheet and Drive workflow around「小龍蝦（115年零用金）openclaw」. Use when the user uploads or mentions a 三聯（手開）進項發票、電子（傳統）發票進項發票、有稅進項發票、其他單據 image, receipt image, or 勞務報酬單 and wants AI to extract ledger fields, confirm missing or uncertain values, classify the document type, ask for the source, write the final data into the target Google Sheet, and upload the image into the matching Google Drive folder.
---

# Lobster Invoice Intake

## Session memory shared rules

Apply these rules to all routing and repeated follow-up questions in this skill.

- Within the same session, if the user has already clearly confirmed a reusable flow decision, continue to use it for later invoices of the same batch and do not ask again.
- If the user later changes that decision in the same session, immediately replace the old value with the new one and continue with the new value.
- Only remember stable workflow choices, not per-invoice values that should be reconfirmed for each document.
- If a newly uploaded invoice clearly belongs to the same ongoing batch, default to the existing flow choice. If it appears to be a new task, a new batch, or the context is unclear, ask again.
- If reusing session memory could cause a wrong write target or wrong categorization, ask instead of assuming.

**This skill must remember within the session:**
- Whether the invoice flow has already been confirmed as the lobster petty-cash workflow
- Whether the invoice flow has already been confirmed as the general reimbursement workflow

**This skill must not assume from prior invoices unless explicitly reconfirmed or clearly visible on the new invoice:**
- Per-invoice extracted fields such as 發票號碼, 品項, 金額, 日期, 統編, category, or source

## Overview

Use this skill for the end-to-end document intake workflow tied to the Google Sheet `小龍蝦（115年零用金）openclaw` and the Google Drive folder with the same name.

The workflow is conversational first: extract from the invoice image or labor-payment document image, show the parsed result in the common ledger field format, ask the user to confirm or fill unknown fields, ask for category, ask for source, then write the final record to Sheets and upload the image to Drive.

## Workflow

Follow this sequence exactly.

### 1. Identify the intake target

Assume these fixed targets unless the user explicitly changes them:

- Google Sheet name: `小龍蝦（115年零用金）openclaw`
- Google Sheet ID: `1c7IENdapgZtwT5xsOTrzZ910mYhU7YkxWdT4PZqO78k`
- Google Drive folder name: `小龍蝦（115年零用金）openclaw`
- Google Drive folder ID: `1pTDhwl2tPZ8cpHR2sY3Ay9-3oxpwWhf4`

If the user later changes the destination, confirm before writing.

### 2. Read and extract the document image

When the user uploads an invoice image or 勞務報酬單 image:

- If this session has already confirmed that subsequent invoice/receipt images should use the lobster petty-cash flow, continue directly and do not ask again.
- If this session has already confirmed that subsequent invoice/receipt images should use the general reimbursement flow, stop this skill and route to `expense-report`.
- If the session has not established a flow yet, and the user only uploads an invoice/receipt image or the message does not clearly indicate whether this belongs to the general reimbursement flow or the lobster petty-cash flow, ask exactly this routing question first:
  「這張單據要走哪個流程？
  1. 一般報帳（實見/益循）
  2. 小龍蝦零用金發票登錄」
- In that unconfirmed state, do not run image analysis, do not extract fields, do not classify the document, and do not show OCR results, guessed fields, or follow-up confirmation in the same reply.
- If the user chooses 1, and this choice is a reply to an already-uploaded image in the current turn context, immediately stop this skill and hand off to `expense-report` as an image-based reimbursement flow, not as manual-entry reimbursement flow.
- If the user chooses 1, record that this session should continue with the general reimbursement flow and stop this skill, routing to `expense-report`.
- If the user chooses 2, and this choice is a reply to an already-uploaded image in the current turn context, immediately continue this skill as an image-based lobster petty-cash flow.
- If the user chooses 2, record that this session should continue with the lobster petty-cash flow and continue this skill.
- Only continue this skill after one of these is true:
  - the user explicitly chooses 2 in this session, or
  - the surrounding text already clearly states that this document belongs to the lobster petty-cash workflow.
- If the image was already uploaded before the routing answer arrived, treat the routing answer as deciding which image-processing branch to continue, not as permission to discard the uploaded image context.
- Do not infer lobster petty-cash routing from the document type alone. A 勞務報酬單, receipt, or invoice image by itself is not enough to skip the routing question.
- After the flow is confirmed as lobster petty-cash, use image analysis to extract visible text and structured fields.
- Always return the extraction in the ledger field format below. Do not stop at raw OCR text, document-title summaries, or free-form field dumps.
- Parse these target fields for ledger entry:
  - 發票號碼
  - 品項
  - 未稅
  - 稅額
  - 總額
  - 收入
  - 餘額
  - 統編
  - 公司名稱
  - 日期
- If the uploaded document is a 勞務報酬單 or similar non-invoice payment slip, still stay in this skill and map the document into the same ledger fields instead of routing elsewhere.
- For 勞務報酬單, extraction is mandatory. Do not reply with only generic OCR results such as 姓名, 身分證字號, 聯絡電話, 地址, 應付總額, 支付淨額 unless those values are being used to derive the ledger fields.
- For 勞務報酬單 mapping, use these defaults unless the user corrects them:
  - 發票號碼: `未知`
  - 品項: 支付事項
  - 未稅: 應付總額
  - 稅額: 代扣稅額，若票面未列或空白則寫 `0`
  - 總額: 應付總額
  - 收入: 支付淨額；若未列則可用實際支付金額或留待使用者確認
  - 餘額: `未知`
  - 統編: 開立單位統編；若影像無法可靠辨識則 `未知`
  - 公司名稱: 開立單位
  - 日期: 領款日期或單據日期
- When the document is a 勞務報酬單, first identify the underlying slip fields needed for mapping, then immediately output the final mapped ledger fields:
  - 發票號碼 = 未知
  - 品項 = 支付事項
  - 未稅 = 應付總額
  - 稅額 = 代扣稅額，空白則 0
  - 總額 = 應付總額
  - 收入 = 支付淨額
  - 餘額 = 未知
  - 統編 = 開立單位統編，辨識不到則 未知
  - 公司名稱 = 開立單位
  - 日期 = 領款日期
- If any mapped field is uncertain, mark only that ledger field as `未知` or ask the user to confirm it. Do not switch back to a raw-OCR-only response format.
- 公司名稱一律擷取並填寫賣方公司的名稱，不使用買方名稱；若票面同時出現買方與賣方資訊，優先取賣方欄位或開立方名稱。
- Preserve uncertainty. Do not invent missing values.
- 統編欄位若發票上同時出現「買方」資訊，預設將「買方」後方的號碼視為統編並擷取；僅在影像真的無法可靠辨識買方號碼時，才標記為 `未知`。
- If a field cannot be read reliably, mark it as `未知` internally and ask the user.

If multiple line items exist:

- Summarize the item list clearly.
- If the sheet requires one combined item string, join line items with `；`.
- If uncertain whether a number is subtotal, tax, or total, ask instead of guessing.

### 3. Return extraction results and ask for confirmation

Only after the user has confirmed that this document should use the lobster petty-cash flow, show the extracted result back to the user before writing anything.

Use a compact confirmation format like this:

- 發票號碼：...
- 品項：...
- 未稅：...
- 稅額：...
- 總額：...
- 收入：...
- 餘額：...
- 統編：...
- 公司名稱（賣方或開立單位）：...
- 日期：...

For 勞務報酬單, keep exactly the same ledger-field confirmation format. Do not replace it with a different set of form fields.

Then ask the user to confirm whether the values are correct.

### 4. Resolve missing or uncertain fields

If any field is unknown, ambiguous, or blank:

- Ask only for the missing fields.
- Keep the questions short and explicit.
- If the user says they do not know, leave that field blank.
- Do not repeatedly ask for a field once the user clearly says they do not know.

Rules:

- `不知道` / `不清楚` / equivalent user replies mean the field should be stored as blank, except for 稅額、總額、餘額, which should be written as `0` when unknown.
- Blank is preferable to fabricated data for other fields.

### 5. Ask for document category

After the extracted fields are confirmed, ask the user which category the document belongs to.

Allowed categories:

- 三聯（手開）進項發票
- 電子（傳統）發票進項發票
- 有稅進項發票
- 其他

For 勞務報酬單, default recommendation is `其他`, but still ask the user to confirm the category instead of assuming.

When asking for category, always provide numbered options so the user can reply with either the number or the text. Use this format:

1. 三聯（手開）進項發票
2. 電子（傳統）發票進項發票
3. 有稅進項發票
4. 其他（我要新增選項）

Rules:
- Accept either numeric replies (`1`, `2`, `3`, `4`) or text replies.
- Normalize near matches such as `電子發票` to `電子（傳統）發票進項發票`.
- If the user chooses `4` or says `其他`, ask one follow-up question asking what category they want to add or use, then use that answer as the final category text.
- If the user replies with both number and text, prioritize the explicit text when they conflict.
- If the reply is still ambiguous, ask once for clarification.
- If the user says `確認` or `1` immediately after a yes/no style confirmation question, treat that as confirmation for that question only, not as category option `1`, unless the current prompt is explicitly the category selection prompt.

### 6. Ask for source

After category is confirmed, ask for source with numbered options when there is a known shortlist available in the current workflow context.

Default source prompt format:

1. 運營
2. 其他（我要新增選項）

Rules:
- Accept either numeric replies (`1`, `2`) or text replies.
- If the user chooses `2` or says `其他`, ask one follow-up question asking what source they want to add or use, then use that answer as the final source text.
- If the user provides source text directly, use it as-is unless they ask for normalization.
- If the user does not know, leave it blank.
- If the user already provided 來源 in the same message batch or during an earlier confirmation for this document, do not ask again.
- If future workflow updates define a larger approved source list, present that list as numbered options and keep the final option as `其他（我要新增選項）`.

### 7. Determine the write target in the sheet

Before writing, inspect the spreadsheet structure.

- Use Google Sheets metadata first to discover tabs.
- Choose the correct worksheet based on the invoice date.
- Default rule: use the month derived from `日期`.
- If the workbook uses month-based tabs, write into the tab matching that month.
- If the workbook structure is unclear, inspect header rows before writing.
- Within the chosen category section, find the topmost row where the 品項 cell is blank and use that row for the write.
- Never guess cell positions without checking the current sheet structure.

Read `references/sheet-mapping.md` before the first write in a session or whenever the workbook layout looks different.

Current known category-to-column mapping for the workbook `小龍蝦（115年零用金）openclaw` / sheet `陳楟蓁零用金`:

Important rule: the first column in each category block is the prefilled 流水號 column. Do not overwrite it. The invoice number must be written into the cell immediately to the right of the 流水號.

- 三聯（手開）進項發票: A:L
  - A: 流水號（保留原值，不可覆蓋）
  - B: 發票號碼
  - C: 品項
  - D: 未稅
  - E: 稅額
  - F: 總額
  - G: 收入
  - H: 餘額
  - I: 統編
  - J: 公司名稱
  - K: 日期
  - L: 來源
- 電子（傳統）發票進項發票: N:Y
  - N: 流水號（保留原值，不可覆蓋）
  - O: 發票號碼
  - P: 品項
  - Q: 未稅
  - R: 稅額
  - S: 總額
  - T: 收入
  - U: 餘額
  - V: 統編
  - W: 公司名稱
  - X: 日期
  - Y: 來源
- 有稅進項發票: AA:AL
  - AA: 流水號（保留原值，不可覆蓋）
  - AB: 發票號碼
  - AC: 品項
  - AD: 未稅
  - AE: 稅額
  - AF: 總額
  - AG: 收入
  - AH: 餘額
  - AI: 統編
  - AJ: 公司名稱
  - AK: 日期
  - AL: 來源
- 其他: AN:AY
  - AN: 流水號（保留原值，不可覆蓋）
  - AO: 發票號碼
  - AP: 品項
  - AQ: 未稅
  - AR: 稅額
  - AS: 總額
  - AT: 收入
  - AU: 餘額
  - AV: 統編
  - AW: 公司名稱
  - AX: 日期
  - AY: 來源

### 8. Write the final data to Google Sheets

Recommended implementation flow for the current workbook layout:

1. Read sheet metadata and confirm the target sheet is still `陳楟蓁零用金`.
2. Select the category block from the confirmed category:
   - 三聯（手開）進項發票 -> A:L, 流水號欄 A, 發票號碼欄 B, 品項欄 C
   - 電子（傳統）發票進項發票 -> N:Y, 流水號欄 N, 發票號碼欄 O, 品項欄 P
   - 有稅進項發票 -> AA:AL, 流水號欄 AA, 發票號碼欄 AB, 品項欄 AC
   - 其他 -> AN:AY, 流水號欄 AN, 發票號碼欄 AO, 品項欄 AP
3. Read enough rows from the target block to find the first blank 品項 cell. Start from the top data region, not just the next visible sequence number.
4. Scan downward row by row within that block:
   - if 品項 is non-empty, continue
   - if 品項 is empty, select that row and stop
5. Preserve the existing 流水號 cell value in the first column of the block. Never overwrite it.
6. Build one full row payload for the chosen block, placing 發票號碼 in the cell immediately to the right of 流水號.
7. Write with `gog sheets update` to the exact block range for that row.
8. Optionally read back the written range once when confidence is low or the sheet layout looked irregular.

Only write after all of the following are complete:

- OCR extraction done
- User confirmation received
- Unknown fields resolved or intentionally left blank
- Category received
- Source received, already provided by the user, or intentionally blank

Write one row per document.

Field handling rules:

- Keep invoice number exactly as shown on the invoice when readable.
- For non-invoice documents such as 勞務報酬單, keep 發票號碼 blank in the final sheet write when the value is unknown, even if the conversational confirmation used `未知`.
- 統編預設取自發票上的「買方」號碼；若同時存在其他號碼，除非使用者另有指定，仍以買方號碼為準。
- 公司名稱一律寫入賣方公司名稱；若僅能辨識品牌名且無法可靠讀出完整法定名稱，先寫可清楚辨識的賣方名稱，必要時向使用者確認。
- Keep date in a sheet-friendly date-only format, for example `2026/3/15`.
- Do not include the time portion in the sheet write unless the user explicitly asks for it.
- Keep numeric fields as plain numeric strings when possible.
- Leave unknown values blank, except 稅額、總額、餘額, which should be written as `0` when unknown.
- Do not overwrite existing rows unless the user explicitly asks for an update.
- Prefer the topmost row in the chosen category block whose 品項 cell is blank.
- Use append workflows only when the sheet is truly row-based and the blank-row rule does not apply.

Before the actual write, restate the final values briefly if there was any ambiguity.
If the sheet section for the chosen category contains a dedicated 發票號碼 column, write the invoice number there.
If the chosen category block has a sequence-number column, do not use that number alone to pick the target row. Use the first row whose 品項 is blank.
If no blank 品項 row is found in the initially read range, read a larger range and continue scanning instead of guessing.

### 9. Upload the invoice image to Google Drive

After the sheet write succeeds:

- Upload the original invoice image to Drive folder `1pTDhwl2tPZ8cpHR2sY3Ay9-3oxpwWhf4`.
- Use a deterministic filename.
- Required filename format:
  - `YYYYMMDD $總額_品項.jpg`
  - Example: `20260315 $1434_九八無鉛.jpg`
- If 品項 contains multiple line items, use the combined sheet item string.
- If 品項 is missing, use `發票` in its place.
- Preserve the original extension when possible.

If upload fails after the sheet write succeeded:

- Tell the user the sheet write succeeded but image upload failed.
- Do not hide partial success.

### 10. Final confirmation to the user

After both actions finish, reply with a concise completion summary:

- 已寫入哪個工作表
- 是否成功上傳圖片
- Any fields that were left blank

## Operational rules

- Do not send data externally except to the target Google Sheet and Google Drive required by this workflow.
- Treat 勞務報酬單 as a first-class supported document type in this workflow, not as an exception or fallback case.
- However, a 勞務報酬單 upload still must follow the same routing gate as any other document when the session flow has not yet been confirmed.
- Confirm before writing only when destination, structure, or parsed data is materially ambiguous.
- If the user has already supplied some ledger fields in text, use them to override or fill OCR results for the same document instead of re-asking.
- Prefer fewer larger Sheets writes over many tiny updates.
- If the user uploads several invoices at once, process them one by one unless they explicitly ask for batch mode.
- If one invoice fails, isolate the failure and continue only with user approval.
- Before replying with extracted results, check that the response is in ledger format and not raw OCR format.

## Suggested tool usage

- Use image analysis for OCR-style extraction from invoice photos and labor-payment document photos.
- Use `gog sheets metadata <sheetId> --json` to inspect tabs.
- Use `gog sheets get` to inspect header rows when mapping columns.
- Use `gog sheets append` or `gog sheets update` depending on workbook structure.
- Use `gog drive search` and upload-capable Drive commands/workflows supported in the environment.

## References

- Read `references/sheet-mapping.md` for the row/column mapping workflow.
- Read `references/conversation-template.md` for the recommended user-facing question flow.
