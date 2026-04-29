# Agent-browser checklist

Use this when executing the BLI drop-insurance flow in the browser.

## CRITICAL: Zero-message start

When this skill triggers, immediately open the browser. Do NOT send any text message before the browser is open. Do NOT ask for disenrollment details (name, ID, date, reason) before the form page is loaded. The ONLY pre-browser question allowed is for missing login credentials (when bli-private.json does not exist).

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
12. Navigate directly to `https://edesk.bli.gov.tw/me/#/cpa/apply/sgl-declare/delete` (skip the function menu)
13. On step 1, keep `勞(就,災)保/勞退` unless told otherwise, then click `下一步`
14. On the data page, ask the user step by step for the insured person data instead of collecting everything up front
15. Normalize ROC-format dates to `YYYMMDD` before filling
16. Open the 退保日期 dropdown, list all visible options, and ask the user to choose
17. Ask about health insurance transfer/withdrawal
18. If health insurance is needed, collect reason category (轉出/退保) and specific reason
19. If no health insurance processing needed, uncheck 健保本人
20. Fill certificate PIN at the end
21. Stop for final confirmation before clicking `申報`, unless the user explicitly asked for final submission

## Execution guidelines

- Prefer one checkpoint per page transition.
- Validate location by URL fragment and visible heading text.
- If a click seems to do nothing, re-check whether the target panel is already open.
- Avoid aggressive retries on the card-reader step.
- Treat final submit as a confirmation boundary.
- Do not fabricate dropdown values when the page can reveal the real options.
- Ask one logical group at a time, not one giant questionnaire unless the user prefers batch input.

## Interactive question order

1. 退保人身分證字號
2. 退保人姓名
3. 退保人出生日期
4. 退保日期（從實際下拉選單讀出）
5. 是否同時健保轉出/退保
6. 若是：原因別（轉出/退保）
7. 若轉出：離職/退休/停歇業/退會/轉換投保單位
8. 若退保：失蹤滿6個月/死亡/喪失健保法第8或第9條資格者
9. 自然人憑證 PIN
10. 最後確認與申報

## Health insurance reason options

### 原因別：轉出

- 離職
- 退休
- 停歇業
- 退會
- 轉換投保單位

### 原因別：退保

- 失蹤滿6個月
- 死亡
- 喪失健保法第8或第9條資格者

## Data handling

Keep credentials and identifiers out of logs and summaries when possible. If you must confirm a value, mask it.
