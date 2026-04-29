# Sheet Mapping

Use this reference to safely map extracted invoice data into the spreadsheet `小龍蝦（115年零用金）openclaw`.

## Fixed workbook identity

- Sheet ID: `1c7IENdapgZtwT5xsOTrzZ910mYhU7YkxWdT4PZqO78k`
- Preferred workflow: inspect first, write second

## Required safety steps

1. Run Sheets metadata and list worksheet titles.
2. Identify the target tab from the invoice date.
3. Read enough top rows to locate headers.
4. Map headers to the final fields before writing.
5. In the chosen category block, locate the topmost row whose 品項 cell is blank.
6. Write the full record into that row.

## Known column mapping for current workbook

For workbook `小龍蝦（115年零用金）openclaw`, sheet `陳楟蓁零用金`, use these category blocks unless the sheet structure changes:

Important rule: the first column of each block is the prefilled 流水號. Keep that original value. Write 發票號碼 into the cell immediately to the right of the 流水號 column.

- 三聯（手開）進項發票: `A:L`
  - A 流水號（保留原值，不可覆蓋）
  - B 發票號碼
  - C 品項
  - D 未稅
  - E 稅額
  - F 總額
  - G 收入
  - H 餘額
  - I 統編
  - J 公司名稱
  - K 日期
  - L 來源
- 電子（傳統）發票進項發票: `N:Y`
  - N 流水號（保留原值，不可覆蓋）
  - O 發票號碼
  - P 品項
  - Q 未稅
  - R 稅額
  - S 總額
  - T 收入
  - U 餘額
  - V 統編
  - W 公司名稱
  - X 日期
  - Y 來源
- 有稅進項發票: `AA:AL`
  - AA 流水號（保留原值，不可覆蓋）
  - AB 發票號碼
  - AC 品項
  - AD 未稅
  - AE 稅額
  - AF 總額
  - AG 收入
  - AH 餘額
  - AI 統編
  - AJ 公司名稱
  - AK 日期
  - AL 來源
- 其他: `AN:AY`
  - AN 流水號（保留原值，不可覆蓋）
  - AO 發票號碼
  - AP 品項
  - AQ 未稅
  - AR 稅額
  - AS 總額
  - AT 收入
  - AU 餘額
  - AV 統編
  - AW 公司名稱
  - AX 日期
  - AY 來源

Re-check metadata and headers if the workbook layout changes.

## Expected business fields

Map as many of these as the workbook supports:

- 發票號碼
- 日期
- 公司名稱
- 統編
- 品項
- 未稅
- 稅額
- 總額
- 收入
- 餘額
- 類別
- 來源
- 圖片檔名 or 圖片連結

## Mapping rules

- Prefer exact header matches.
- If no exact match exists, use obvious semantic matches.
- If multiple candidate columns exist, inspect nearby headers and sample rows before choosing.
- If the sheet uses merged title rows, skip those and find the actual header row.
- If no safe mapping can be determined, stop and ask the user.

## Month tab selection

Default heuristic:

- Parse the invoice date.
- Match the tab for that month.
- Accept common naming variants such as:
  - `1月`, `01月`
  - `2026-01`
  - `2026年1月`
  - `115-01`
  - `115年1月`

If multiple tabs could match, inspect both and choose the one whose headers align with invoice logging.

## Writing strategy

Preferred order:

1. `gog sheets metadata <sheetId> --json`
2. Confirm the category block and its key columns:
   - 三聯（手開）進項發票: block `A:L`, 流水號 `A`, 發票號碼 `B`, 品項 `C`
   - 電子（傳統）發票進項發票: block `N:Y`, 流水號 `N`, 發票號碼 `O`, 品項 `P`
   - 有稅進項發票: block `AA:AL`, 流水號 `AA`, 發票號碼 `AB`, 品項 `AC`
   - 其他: block `AN:AY`, 流水號 `AN`, 發票號碼 `AO`, 品項 `AP`
3. `gog sheets get <sheetId> "<tab>!<blockStartRow>:<blockEndCol><enoughRows>" --json` and inspect enough rows to find the first blank 品項 cell in that category block
4. Scan from top to bottom and select the first row where 品項 is blank
5. Preserve the existing 流水號 value in the first column of the target row
6. Build the full row payload for that category block, placing 發票號碼 in the cell immediately to the right of 流水號
7. `gog sheets update ... --values-json ...` to write the exact range for that row
8. Use `gog sheets append ...` only for truly row-based sheets that do not have preallocated category blocks

## Suggested execution pattern

Use this pattern when the workbook matches the known layout:

1. Read the target block, for example `陳楟蓁零用金!N2:Y60` for the electronic invoice block.
2. Use the sequence-number cell only as a preserved existing value, never as a writable target for 發票號碼.
3. Inspect only the 品項 column in that block when selecting the row.
4. Pick the first row where 品項 is empty.
5. Write the full row into that exact block range, preserving the first cell's 流水號 and placing 發票號碼 in the next cell, for example `N13:Y13`.
6. If no blank row is found, expand the read range and continue scanning.
7. If the block headers no longer match the known mapping, stop and re-validate before writing.

## Missing values

If the user does not know a field:

- Write blank for most fields
- Write `0` for 稅額、總額、餘額 when those values are unknown
- Do not write placeholder text like `未知` unless the sheet already uses that convention

## Validation before write

Before writing, ensure:

- invoice number is mapped to the cell immediately to the right of the preserved 流水號 column
- the original 流水號 cell remains unchanged
- the selected row is the topmost row in that category block whose 品項 is blank
- date is in the correct tab
- date is written as date only, for example `2026/3/15`, without time
- amounts are aligned with the intended columns
- category and source columns are included if present
- the image upload plan is clear
- the chosen category uses the expected block mapping above, or you have re-validated a changed layout
