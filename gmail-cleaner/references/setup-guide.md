# Gmail API 初次設定指南

## 步驟一：建立 Google Cloud 專案

1. 前往 https://console.cloud.google.com/
2. 建立新專案（或選擇現有專案）
3. 啟用 **Gmail API**：
   - 左側選單 → APIs & Services → Library
   - 搜尋 "Gmail API" → 點選 Enable

## 步驟二：建立 OAuth 憑證

1. 左側選單 → APIs & Services → Credentials
2. 點選「+ Create Credentials」→「OAuth client ID」
3. Application type 選「Desktop app」
4. 下載 JSON 檔案，重新命名為 `credentials.json`
5. 放置到 `~/Wu/gmail/credentials.json`

## 步驟三：設定 OAuth 同意畫面

1. 左側選單 → OAuth consent screen
2. User Type 選「External」
3. 填入應用程式名稱（例如：Gmail Cleaner）
4. 在 Scopes 加入：
   - `https://www.googleapis.com/auth/gmail.modify`
5. 在 Test users 加入自己的 Gmail 帳號

## 步驟四：安裝 Python 套件

```bash
pip3 install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## 步驟五：首次授權

在執行 OpenClaw / gmail-cleaner 的同一台電腦上執行：

```bash
python3 skills/gmail-cleaner/scripts/gmail_auth.py
```

完成瀏覽器登入後，`token.json` 會自動儲存到 `~/Wu/gmail/token.json`。

## 步驟六：後續維護

- `credentials.json` 是 OAuth 應用程式設定，通常長期不變
- `token.json` 是實際登入授權，之後執行模式 A / B 會優先用它自動續期
- 正常情況下不需要每次重新授權
- 只有在以下情況才需要重跑授權：
  - 你手動撤銷 Google 帳號對此 App 的權限
  - 更換了 `credentials.json`
  - `token.json` 損壞或 refresh token 失效

## 常見問題

### 為什麼會看到 localhost 無法連線？
這代表 OAuth 授權的瀏覽器不在執行腳本的同一台電腦上，或該電腦無法接收 localhost callback。

解法：
- 請在執行腳本的同一台電腦上開啟授權網址完成登入
- 不要在手機、遠端桌面外的其他裝置完成最後授權步驟
