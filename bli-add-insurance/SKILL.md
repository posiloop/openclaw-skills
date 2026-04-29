---
name: bli-add-insurance
description: >
  CRITICAL: When this skill triggers, your FIRST action MUST be a tool call to open the browser — do NOT send any text message first.
  Automate Taiwan BLI employer-side add-insurance enrollment (加保作業) through the 勞保局 e 化服務系統 using browser automation.
  Use when the task involves logging into https://edesk.bli.gov.tw/me, navigating 投保單位網路申報及查詢作業, using 自然人憑證 login,
  handling card-reader checks, then navigating directly to the add-insurance page via URL, or filling the first-step and applicant-data forms for enrollment.
  REMINDER: Do NOT ask the user for any enrollment details (name, ID, dates, salary) before the system is open. Open browser FIRST.
allowed-tools: mcp__claude-in-chrome__*
---

# BLI Add Insurance

## ABSOLUTE RULE — Zero-message start (NO EXCEPTIONS)

> **Your FIRST action when this skill triggers MUST be a tool call. NOT a text message.**
>
> Any text reply before the browser is open and the add-insurance form is loaded is a violation.
> This includes: asking for name, ID, date, salary, greeting, summarizing, confirming, or ANY other text.
>
> The ONLY exception: if `bli-private.json` does not exist, you may ask for login credentials.
> Everything else — every single enrollment detail — is asked AFTER the form page is open.

### Pre-flight self-check (MANDATORY — execute before generating ANY response)

Before you produce any output at all, run this checklist in your head:

1. Is my first output going to be a tool call (read file / open browser via claude-in-chrome)? → GOOD, proceed.
2. Is my first output going to be a text message to the user? → STOP. That is a violation. Change your plan to start with a tool call instead.
3. Am I about to ask for 身分證字號, 姓名, 出生日期, 加保日期, 薪資, or ANY enrollment detail? → STOP. The system is not open yet. You cannot ask these until the add-insurance form page is loaded.

This self-check applies every single time this skill is triggered. No exceptions. No "I'll just quickly ask first". No "讓我先確認". Open the browser. That is step one. Always.

### Why this rule exists

The add-insurance form has date dropdowns and other controls whose available options can only be known by reading the live page. Asking the user for details before the system is open leads to wrong assumptions (e.g. guessing which dates are available). The correct flow is: open system first, read the live form controls, then ask the user to choose from the real options.

### Decision gate (execute this logic, do not skip)

1. Does `~/.openclaw/workspace/state/bli-private.json` exist?
   - YES → your very first action is `navigate to "https://edesk.bli.gov.tw/me/#/home" using claude-in-chrome`
   - NO → ask the user for login credentials only, then open the browser
2. There is no step 2 before the browser is open. Do not send any other message.

### What counts as a violation

- Sending "請提供加保人員資料" before the browser is open → VIOLATION
- Sending "好的，請提供以下資料：1. 身分證字號 2. 姓名..." before the browser is open → VIOLATION
- Sending "請問要加保的人員：1. 姓名 2. 身分證字號..." before the form is loaded → VIOLATION
- Sending "收到，我先確認一下資料" before the browser is open → VIOLATION
- Sending ANY text message as your first response (other than asking for missing login credentials) → VIOLATION
- Sending a short acknowledgment like "好的" or "收到" followed by questions → VIOLATION

### What "just start" means concretely

- CORRECT first action: read `bli-private.json`, then use `tabs_context_mcp` + `navigate` to open `https://edesk.bli.gov.tw/me/#/home` in local Chrome
- WRONG first action: any text message to the user about enrollment details
- The user already told you they want to add insurance. That is sufficient. Go.

## Overview

Execute the employer-side BLI add-insurance flow using the local Chrome browser (via claude-in-chrome MCP tools), while explicitly pausing for native browser or OS permission prompts that the automation may not be able to control.

Prefer this skill when the user wants the enrollment flow turned into a repeatable browser procedure or a semi-automated runbook.

This skill should open the live system proactively and only message the user when input or a real blocker is needed.

Default behavior: **always log into the system and navigate to the add-insurance data page first, before asking the user any enrollment questions.** Do not ask for insured-person details (name, ID, dates, salary, etc.) until the system is open and the add-insurance form is loaded. The only exception is login credentials — if `bli-private.json` is missing, ask for those first since they are required to enter the system.

Once the add-insurance data page is open, continue with the interview-first, fill-later workflow: inspect the live date dropdown, collect all required answers from the user, normalize them, present one consolidated summary for user confirmation, and once the user confirms the summary is correct, proceed directly to fill and submit the web form in the same run unless the user explicitly asked for draft-only preparation. Do not start entering the insured-person form field-by-field while the interview is still in progress unless the user explicitly asks for live incremental entry.

## Workflow

### 1. Confirm login credentials only

Before touching the site, confirm or infer **only login credentials**. Do not ask for any insured-person details at this stage:

- 身分證號
- 保險證號
- 自然人憑證密碼（PIN）

Prefer reading login credentials from the workspace private file `~/.openclaw/workspace/state/bli-private.json` if it exists. Expected structure:

```json
{
  "bli": {
    "idNumber": "...",
    "insuranceNumber": "...",
    "naturalCertificatePin": "..."
  }
}
```

If that file is missing or incomplete, ask the user only for the missing login values. Otherwise proceed straight into the site without a heads-up message.

**Do not ask for insured-person information (name, ID number, birth date, salary, etc.) before the system is open.** All enrollment questions happen after login and navigation to the add-insurance form.

Treat all credentials and personal identifiers as sensitive. Do not place them in SKILL.md, references, packaged `.skill` files, or git-tracked artifacts. Do not echo them back unless needed for confirmation.

### 2. Open the BLI portal

Navigate to:

- `https://edesk.bli.gov.tw/me/#/home`

Then click:

- `投保單位網路申報及查詢作業`

If a pre-login announcement appears, click:

- `Close`

### 3. Choose login method

On the login page, select:

- `自然人憑證`

### 4. Run card-reader detection, then continue immediately

Always click:

- `檢測讀卡機`

Once the login page is open, do not stop to ask whether a native permission dialog appeared. Continue directly to fill the login fields and submit.

Only react to native browser or OS prompts if they actually block progress after submission or clearly prevent the site from continuing.

### 5. Fill login fields

Fill the login form from `state/bli-private.json` when available. Otherwise use values supplied by the user.

Fields:

- 身分證號
- 保險證號
- 自然人憑證密碼（PIN）

Then click:

- `送出`

After clicking `送出`, wait about 10 seconds before judging the result. This site often stays on the same visible login screen for several seconds before completing the redirect.

If the page still appears unchanged during that wait, do not immediately assume login failed. First allow the full 10-second wait to finish before deciding whether retry or troubleshooting is needed.

Only if progress is still blocked should you then check whether the browser or macOS showed a native certificate, card-reader, or external-app confirmation that the automation could not click.

Successful login should land on:

- `https://edesk.bli.gov.tw/me/#/cpa/home`

After the successful login redirect appears, wait about 5 seconds before taking the next action or judging the page state. This reduces flaky behavior where the session can momentarily look stuck around announcement-style overlays or incomplete post-login rendering.

If a post-login guide appears with `歡迎來到新手導覽`, click:

- `略過導覽`

### 6. Navigate to the add-insurance page

After successful login, navigate directly to the add-insurance page by visiting:

- `https://edesk.bli.gov.tw/me/#/cpa/apply/sgl-declare/create`

Do not use the left-side function menu. Direct URL navigation is faster and avoids flaky menu rendering issues in snapshots.

### 7. Complete add-insurance step 1

On the first add-insurance screen, the default option is usually:

- `勞(就,災)保/勞退`

If there is no special case or user override, leave the default selection and click:

- `下一步`

### 8. Run the interactive add-insurance interview

The add-insurance data page should now be open. **This is the earliest point at which you ask the user for insured-person details.** Collect information in this exact conversational order.

Default mode is interview-first, fill-later:

1. ask the questions in staged conversational chunks
2. normalize all dates and selections
3. compile the full planned entry set
4. ask the user to confirm that everything is correct
5. only after that confirmation, begin filling the form

Do not ask for everything in one large block unless the user explicitly prefers that.
Do not start filling the insured-person form as each answer arrives in routine operation.

#### 8.1 Ask for core insured-person fields first

Ask the user for:

- 加保人身分證字號
- 加保人姓名
- 加保人出生日期

Completely ignore the 性別 field. Do not read, click, set, verify, or interact with the sex radio buttons in any way. The system may or may not auto-fill this field — it does not matter. Submissions succeed regardless of whether 性別 is populated. Treat this field as if it does not exist.

Birth date must be entered in ROC format `YYYMMDD`.

Examples:

- 民國 76 年 3 月 11 日 → `0760311`
- 1987-03-11 → `0760311`
- 1987/3/11 → `0760311`
- 19870311 → `0760311`

If the user provides a natural-language ROC date, normalize it before filling.
If the user provides a Gregorian date, convert it to ROC format before filling.

#### 8.2 Always open the live system and read the full 加保日期 list before asking

For every add-insurance case, always navigate into the live add-insurance data page immediately and inspect the page's current 加保日期 control before asking the user to choose a date.

Do not accept, confirm, summarize, paraphrase, or rely on any user-provided 加保日期 before the live dropdown has been opened and its options have been read from the page.

Open the 加保日期 dropdown in the page first.

Read the complete list of actual date options shown in the system dropdown.

List all actual system-provided date options to the user, with no omissions.

Then append one extra option at the end:

- `夜間到職（提供前一工作日十七時後至二十四時前到職用）`

Ask the user to choose from that full presented list.

If the user already gave a date earlier, treat it only as a hint. Still open the live system, read the full dropdown list first, list every available system date option, and only then confirm which listed option should be used.

Never replace the real list with shorthand such as `今天` or `明天`, never collapse multiple system dates into informal labels, and never present a partial subset when the dropdown shows more options.

Do not invent date options, skip the live dropdown read, or assume the user-supplied date is selectable without checking the live page control first.

#### 8.3 Ask for 特殊身份別

Always present the full option list with both code and meaning. Do not ask the user to reply with only a code unless the meanings were already shown in the same message.

Present these options to the user:

- `0：無`
- `1：部分工時人員`
- `3：董事（實際從事勞動）`
- `4：受委任工作者`
- `5：雇主（單位負責人）`
- `A：功法救助及部分工時人員`
- `B：功法救助`
- `S：建教生及部分工時人員`
- `T：建教生`

When asking, prefer a format that includes each code together with its meaning in the same message, so the user does not need to ask what the codes mean.

If the user answers `無`, skip filling this field when the page behavior allows leaving it blank. Otherwise select the matching option.

#### 8.4 Ask for 月薪資總額

Ask the user for the insured person’s monthly total salary amount.
Do not fill it yet in the default workflow. Save it for the final consolidated entry pass after confirmation.

### 9. Handle the labor pension section

After the salary field, move to the 勞退 section and ask these in order.

**雇主提繳率：絕對不要修改此欄位。** 系統會自動帶入預設值（通常為 6%），無論任何情況都不得清空、覆寫或變更此欄位的值。在填寫流程中完全跳過此欄位，當作它不存在。

#### 9.1 個人自願提繳率

Ask whether the user wants to fill 個人自願提繳率.

- If yes, ask for the numeric rate and record it.
- If no, record that it should be left blank.

#### 9.2 勞退提繳日期是否不同

Ask whether 勞退提繳日期 differs from the （勞/退/災）加保日.

- If different, ask for the 勞退提繳日期 and record it.
- If same, record that the field should remain aligned with the add-insurance date.

Use the same ROC date format rule as birth date: `YYYMMDD`.

### 10. Handle health insurance choices

Ask whether the user also wants to add 健保 for the insured person.

- If yes, ask for `合於健保投保日期` and record it using ROC format `YYYMMDD`.
- If no, record that the 健保本人 option should be unchecked.

In routine cases, set `合於健保投保條件` to `到職起薪` by default.
Do not stop to ask the user to confirm `合於健保投保條件` unless the user explicitly asks to change it or the stated scenario is clearly incompatible with `到職起薪`.

### 11. Handle dependent health-insurance enrollment

Ask whether the user wants to申報眷屬加保.

If no, continue onward.

If yes, collect dependent entries one by one.

For each dependent, ask for:

- 姓名
- 身分證號
- 出生日期（ROC format `YYYMMDD`）
- 稱謂代號
- 合於健保投保條件
- 合於健保投保日期（ROC format `YYYMMDD`）

#### 11.1 稱謂代號 options

Present these options:

- 配偶
- 父母
- 子女
- 祖父母
- 孫子女
- 外祖父母
- 外孫子女
- 曾祖父母
- 外曾祖父母

#### 11.2 合於健保投保條件 options

Present these options:

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

#### 11.3 Dependent entry loop

During the interview phase, collect all dependent entries first.

After the user confirms the full submission summary is correct:

1. click `申報眷屬加保`
2. wait for the new dependent-entry block to appear
3. fill the dependent fields
4. click `新增`

Then add the next confirmed dependent entry the same way until all confirmed dependents have been entered.

### 12. Confirm first, then fill, then submit

Before typing into the insured-person form, present a concise but complete summary of all planned entries to the user and ask for explicit confirmation.

Default behavior after that confirmation: do not stop again. Continue in the same run to:

1. fill all insured-person fields
2. fill any dependent entries
3. fill the 自然人憑證密碼
4. click `申報`
5. wait for the result page or success indicator
6. report the submission result to the user
7. close the browser tab (use `computer` `action: key` `text: "cmd+w"`)

Only add an extra pre-submit pause if the user explicitly asked for draft-only preparation, navigation-only help, or a final manual review before submission.

### MANDATORY: Post-submission receipt download

After a **successful** submission, do NOT close the browser immediately. First, download the 加保單 receipt and upload it to Google Drive, then report the Drive link to the user. Only after that may the tab be closed.

Sequence (執行順序):

1. **Navigate to the rudp query page**
   - `navigate` to `https://edesk.bli.gov.tw/me/#/cpa/apply/rudp`
   - `wait` 3 seconds

2. **Click the 查詢 button**
   - `find` the 查詢 button on the page, `computer` `left_click` it
   - `wait` 3 seconds for the result page to load

3. **Click the correct category button (加保 side)**
   - On the result page, find the 加保 section
   - In that section, `find` and click the `勞(就)保/災保/勞退` button
   - `wait` 3 seconds

4. **Find and select the just-submitted record**
   - The page shows a list of add-insurance records
   - Identify the row that matches the data just submitted (use 姓名 + 身分證字號 + 加保日期 to match uniquely)
   - `find` and click the checkbox for that row to select it

5. **Click 明細查詢**
   - `find` and click the 明細查詢 button
   - `wait` 3 seconds for the detail page

6. **Click 下載 to download the 加保單**
   - `find` and click the 下載 button
   - `wait` 5 seconds for the download to complete
   - The file typically lands in `~/Downloads` with a name like `加保單_*.pdf`; use a Bash `ls -t ~/Downloads | head -3` to locate the newest file

7. **Upload to Google Drive**
   - Run: `gog drive upload "<downloaded file path>" --parent 1bPwoQXjixXz9jOoqXx3N5PaIvmXker99`
   - The folder `1bPwoQXjixXz9jOoqXx3N5PaIvmXker99` is the "加退保申報表" folder in the user's Drive
   - Capture the uploaded file's ID from the command output
   - Run `gog drive url <fileId>` to get the shareable URL

8. **Report the Drive link to the user** via Telegram reply

9. **Only now close the BLI session:**
   - `computer` `action: key` `text: "cmd+w"` to attempt tab close
   - If the tab still shows `edesk.bli.gov.tw` via `tabs_context_mcp`, `navigate` to `https://www.google.com` to unload the sensitive page
   - Optionally ask the user to manually close the tab if cmd+w didn't work

If the submission **failed** (not success), skip steps 1–8 and go straight to step 9. There is no receipt to download for a failed submission.

This sequence is mandatory on every successful add-insurance submission — the user always wants the receipt archived to Drive.

## Field formatting rules

### ROC date normalization

For all applicable date fields, use ROC format `YYYMMDD`.

This includes:

- 出生日期
- 勞退提繳日期
- 合於健保投保日期
- 眷屬出生日期
- 眷屬合於健保投保日期

Examples:

- 民國 76 年 3 月 11 日 → `0760311`
- 1987-03-11 → `0760311`
- 1987/3/11 → `0760311`
- 19870311 → `0760311`

When the user gives a date in spoken or written Chinese, convert it before filling.
When the user gives a Gregorian date, subtract 1911 from the year and convert it to ROC format `YYYMMDD` before filling.
Preserve leading zeros for month and day, and use a 3-digit ROC year when needed.

### Sensitive values

Mask or avoid repeating:

- 身分證字號
- 保險證號
- 自然人憑證 PIN

## Submission safety rule

Treat the user's request to 「幫我加保」, or any equivalent clear request to execute the add-insurance task, as authorization to complete the submission after the collected dataset has been summarized and explicitly confirmed by the user.

In the default workflow, do not begin filling the insured-person form until the user has reviewed and confirmed the complete collected dataset.

If the user asked only for navigation, draft entry, or explicitly said not to submit, stop before clicking `申報` and report the current state.

## Browser execution notes (claude-in-chrome)

**Always use the local Chrome browser via `mcp__claude-in-chrome__*` MCP tools.** Do NOT use agent-browser (headless). The local Chrome has the BLIePKI software and card reader access needed for 自然人憑證 login.

### Tool mapping

| Action | Tool | Method |
|--------|------|--------|
| Get tab context | `tabs_context_mcp` | Call with `createIfEmpty: true` at start |
| Create new tab | `tabs_create_mcp` | Creates tab in MCP group |
| Navigate | `navigate` | Pass URL and tabId |
| Find elements | `find` | Natural language query to locate elements |
| Click | `computer` | `action: left_click` with ref or coordinate |
| Type text | `computer` | `action: type` with text |
| Press key | `computer` | `action: key` with key name (e.g. "Tab") |
| Screenshot | `computer` | `action: screenshot` |
| Wait | `computer` | `action: wait` with duration |
| Scroll | `computer` | `action: scroll` with direction |
| Set dropdown | `form_input` | Pass ref and value for select elements |
| Read DOM | `javascript_tool` | Execute JS to read dropdown options etc. |
| Close tab | `computer` | `action: key` with "cmd+w" |

### Critical: form filling method

This site is built with Angular. **Never use `javascript_tool` to set form field values directly.** Even if the value appears on screen, Angular's internal form model will not register the change, and the field will fail validation on submit (showing 必填 errors despite having a visible value).

**Always use `computer` with `action: type` to fill every text input.** Click the field first with `computer` `action: left_click`, then type the value. After filling each field, use `computer` `action: key` with `text: "Tab"` to trigger blur/change events and ensure Angular validation runs.

For `<select>` dropdowns, use `form_input` with the ref from a `find` query. Do not set select values via `javascript_tool`.

The same rule applies to the login form and all other forms on this site.

### Workflow guidelines

- **always log in and navigate to the add-insurance form before asking the user any enrollment questions** — the only pre-login question allowed is for missing login credentials
- start the live system proactively once the task is clear, without sending a courtesy notice first unless input or a blocker requires it
- use small, checkpointed actions instead of one huge prompt
- after each page transition, verify page identity via tab context URL or screenshot
- treat `檢測讀卡機` as a normal default action first, then continue directly with filling and submitting the login form
- after detecting a successful redirect into the post-login page, wait about 5 seconds before interacting further so transient overlays or incomplete rendering do not get mistaken for blockers
- only call out manual intervention if a native permission prompt later proves to be blocking progress
- completely ignore the 性別 (sex) radio buttons — do not read, fill, click, or verify them; submissions succeed without this field
- on the add-insurance data page, prefer conversational collection in stages, but keep the default behavior as collect-first and fill-after-confirmation
- for every case, open the live system and inspect the 加保日期 dropdown before asking the user to choose a date
- to read dropdown options, use `javascript_tool` to extract all `<option>` text from select elements
- read the full system-provided 加保日期 list and present every displayed date option to the user before asking them to choose
- never compress those system date options into shorthand like `今天` or `明天`
- when asking users to choose coded options such as `特殊身份別`, always show the code together with the full meaning in the same message rather than listing bare codes only
- if the site becomes inconsistent, recover by checking whether the current page is home, login, post-login home, or add-insurance form before continuing

### Practical execution rhythm

1. call `tabs_context_mcp` with `createIfEmpty: true` to get a tab
2. `navigate` to `https://edesk.bli.gov.tw/me/#/home`
3. `find` and click `投保單位網路申報及查詢作業`
4. `find` and click `Close` if announcement modal appears
5. on login page, `find` and click `檢測讀卡機`
6. `find` each login field (身分證號, 保險證號, PIN), click and type values using `computer`, press Tab after each
7. `find` and click `送出`, then `wait` 10 seconds for post-login redirect
8. once on `/cpa/home`, `wait` 5 seconds, then `find` and click `略過導覽` if present
9. `navigate` directly to `https://edesk.bli.gov.tw/me/#/cpa/apply/sgl-declare/create`
10. `find` and click `下一步`
11. use `javascript_tool` to read all `<select>` dropdown options (加保日期, 特殊身分別, etc.)
12. ask user for insured-person data in stages
13. after user confirms the full summary, `find` each field, click and type values, use `form_input` for dropdowns; **never touch 雇主提繳率 — leave its system default**; fill certificate PIN last
14. click `申報` and `wait` for result
15. report result to user, then close the tab with `computer` `action: key` `text: "cmd+w"`

## Reference files

Read `references/flow.md` when you need the concise canonical click path, field list, and failure points during implementation or review.

Read `references/agent-browser-checklist.md` when you need a direct browser-automation checklist or want a prompt skeleton for agent-browser.
