# Agent-browser checklist

Use this when executing the BLI add-insurance flow in the browser.

## Prompt skeleton

Ask the browser agent to:

1. Open `https://edesk.bli.gov.tw/me/#/home`
2. Click `投保單位網路申報及查詢作業`
3. If an announcement modal appears, click `Close`
4. Select login method `自然人憑證`
5. Click `檢測讀卡機`
6. Pause if a native browser or OS permission prompt appears, and ask the user to approve it manually
7. Fill 身分證號, 保險證號, and PIN
8. Click `送出`
9. Wait about 5 seconds, then check for URL or page state matching `/cpa/home`
10. After the successful post-login page appears, wait about 5 more seconds before further interaction to avoid transient announcement-style overlays or incomplete rendering
11. If `歡迎來到新手導覽` appears, click `略過導覽`
12. Navigate directly to `https://edesk.bli.gov.tw/me/#/cpa/apply/sgl-declare/create` (skip the function menu)
13. On step 1, keep `勞(就,災)保/勞退` unless told otherwise, then click `下一步`
14. On the data page, ask the user step by step for the insured person data instead of collecting everything up front
15. Normalize ROC-format dates to `YYYMMDD` before filling
16. Open the 加保日期 dropdown, list all visible options, append `夜間到職`, and ask the user to choose
17. Ask for 特殊身份別, 月薪資總額, 勞退資訊, 健保資訊, and 眷屬資料 in order
18. For each dependent, click `申報眷屬加保`, fill the new block, then click `新增`
19. Fill certificate PIN at the end
20. Stop for final confirmation before clicking `申報`, unless the user explicitly asked for final submission

## Execution guidelines

- Prefer one checkpoint per page transition.
- Validate location by URL fragment and visible heading text.
- If a click seems to do nothing, re-check whether the target panel is already open.
- Avoid aggressive retries on the card-reader step.
- Treat final submit as a confirmation boundary.
- Do not fabricate dropdown values when the page can reveal the real options.
- Ask one logical group at a time, not one giant questionnaire unless the user prefers batch input.

## Interactive question order

1. 加保人身分證字號
2. 加保人姓名
3. 加保人出生日期
4. 加保日期（從實際下拉選單讀出）
5. 特殊身份別
6. 月薪資總額
7. 是否填個人自願提繳率
8. 勞退提繳日期是否不同
9. 是否同時加保健保
10. 是否申報眷屬加保
11. 若有眷屬，逐筆收集並新增
12. 自然人憑證 PIN
13. 最後確認與申報

## Fixed option sets

### 特殊身份別

- `0：無`
- `1：部分工時人員`
- `3：董事（實際從事勞動）`
- `4：受委任工作者`
- `5：雇主（單位負責人）`
- `A：功法救助及部分工時人員`
- `B：功法救助`
- `S：建教生及部分工時人員`
- `T：建教生`

### 眷屬稱謂代號

- 配偶
- 父母
- 子女
- 祖父母
- 孫子女
- 外祖父母
- 外孫子女
- 曾祖父母
- 外曾祖父母

### 合於健保投保條件

- 隨同被保險人加保
- 喪失被保險人身份
- 結婚
- 收養
- 新增嬰兒
- 更換所依附之被保險人
- 在學就讀且無職業（在學無業）
- 受禁治產宣告尚未撤銷（禁治產宣告）
- 領有殘障手冊而不能自謀生活（殘障不能謀生）
- 罹患重大傷病且無職業（重傷病無業）
- 應屆畢業或服兵役退伍且無職業

## Data handling

Keep credentials and identifiers out of logs and summaries when possible. If you must confirm a value, mask it.
