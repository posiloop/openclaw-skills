---
name: gmail-cleaner
description: "Gmail 垃圾郵件清理工具。管理並刪除 Gmail inbox 中的垃圾郵件，更新垃圾郵件黑名單與特徵規則。模式 A：依黑名單/特徵掃描 inbox，列出候選垃圾郵件讓使用者審核後刪除。模式 B：分析垃圾信箱，與現有規則比對，提出新規律供使用者確認後更新。Use when: user wants to clean Gmail inbox spam, update spam blacklist/feature rules, or review/delete spam emails in Gmail."
---

# Gmail Cleaner Skill

## 設定與前置作業

### 所需憑證
- **credentials.json**：放在 `~/Wu/gmail/credentials.json`（從 Google Cloud Console 下載）
- **token.json**：首次授權後自動產生於 `~/Wu/gmail/token.json`，後續主要靠它自動續期，不需每次重新授權

### 黑名單與特徵檔案
- **黑名單**：`~/Wu/gmail/blacklist.json`（寄件者黑名單）
- **特徵檔案**：`~/Wu/gmail/spam_features.json`（垃圾郵件特徵）

詳見 [references/file-formats.md](references/file-formats.md)

### 初次設定
若 `credentials.json` 不存在，引導使用者至 [Gmail API 設定說明](references/setup-guide.md)

### 授權維護
- 第一次使用時，執行 `python3 skills/gmail-cleaner/scripts/gmail_auth.py` 產生 `token.json`
- 平常執行 `gmail_cleaner.py` 時會優先使用 `token.json` 自動續期
- 若 `token.json` 的 refresh token 被 Google 撤銷或過期，才需要重新授權一次

---

## 工作流程

### 啟動
1. 確認 `~/Wu/gmail/` 目錄與必要檔案存在
2. 確認 `token.json` 可用，若失效則先執行重新授權
3. 詢問使用者選擇模式：A（刪除垃圾郵件）或 B（更新黑名單/特徵）

---

## 模式 A — 刪除垃圾郵件

```
python3 skills/gmail-cleaner/scripts/gmail_cleaner.py scan
```

流程：
1. 讀取 `blacklist.json` 與 `spam_features.json`
2. 掃描 inbox，比對規則，輸出候選垃圾郵件清單
3. 顯示清單（寄件者、主旨、日期、匹配規則）給使用者審核
4. 使用者確認後執行刪除（移至垃圾桶）

顯示格式（ASCII 表格）：
```
+---+----------------------+------------------------+------------+-----------+
| # | 寄件者               | 主旨                   | 日期       | 匹配規則  |
+---+----------------------+------------------------+------------+-----------+
| 1 | noreply@example.com  | 限時優惠！             | 2026-03-27 | 黑名單    |
+---+----------------------+------------------------+------------+-----------+
```

刪除確認選項：
- `all`：全部刪除
- `1,3,5`：指定編號刪除
- `none`：取消

---

## 模式 B — 分析近一個月垃圾郵件高頻項目

```
python3 skills/gmail-cleaner/scripts/gmail_cleaner.py analyze
```

流程：
1. 讀取垃圾筒與垃圾信箱資料
2. 只分析近一個月的郵件
3. 統計最高頻出現的 email、主旨關鍵字、內文關鍵字
4. 將排行結果回報給使用者，供後續決定是否更新黑名單或特徵

---

## 腳本說明

| 腳本 | 用途 |
|------|------|
| `scripts/gmail_cleaner.py` | 主程式（scan / analyze 模式） |
| `scripts/gmail_auth.py` | Gmail OAuth 驗證模組 |
