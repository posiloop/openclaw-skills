# Static Web Deploy — 完整流程

## 環境常數

- Development 根目錄：`~/Development`
- 主機內部 IP：透過 `ifconfig` 查詢（預設 192.168.0.108）
- 公共固定 IP：`220.135.50.87`
- Router 後台：`http://192.168.0.1`（密碼：Aemass160220）

---

## Step 1：詢問專案名稱

詢問使用者：「請問這個專案要命名為？」

### 命名規則（嚴格執行）

- 禁止空白、特殊字元 → 替換為 `-`
- 必須為英文（若使用者給中文，請翻譯後再套用命名規則）
- 合法範例：`my-portfolio`、`pitch-check-web`、`todo-app`

### 重複名稱處理

```bash
ls ~/Development/
```

若已存在同名資料夾，提醒使用者並要求重新命名，循環直到不重複為止。

---

## Step 2：建立專案資料夾並複製檔案

```bash
mkdir -p ~/Development/<project-name>
```

將使用者上傳的所有檔案依照相對路徑關係複製至該資料夾。
注意：所有檔案名稱同樣禁止空白或特殊字元，必要時自動重新命名。

---

## Step 3：尋找可用 Port

```bash
# 查詢已使用的 port
ss -tlnp | awk '{print $4}' | grep -oP ':\K[0-9]+' | sort -n | uniq
```

從 3000 開始往上找第一個未被使用的 port，記為 `<PORT>`。

---

## Step 4：http-server 測試

```bash
cd ~/Development/<project-name>
npx http-server . -p <PORT> --cors -o
```

或確認 http-server 是否已全域安裝：

```bash
which http-server || npm install -g http-server
http-server . -p <PORT> --cors
```

以 `curl -s http://localhost:<PORT>` 或 `curl -s http://localhost:<PORT>/index.html` 驗證回應是否正常（HTTP 200）。

### 測試要點

- 確認 `index.html` 可正常載入
- 檢查 console 錯誤（404 資源缺失、JS 語法錯誤等）

---

## Step 5：Bug 修復（如有需要）

若 Step 4 發現錯誤，使用 Claude Code 進行修復：

```bash
cd ~/Development/<project-name>
claude --permission-mode bypassPermissions --print '請修復以下問題：<錯誤描述>。修復後確認 index.html 可正常運行。'
```

修復後重複 Step 4 測試，直到無錯誤為止。

---

## Step 6：pm2 背景運行

確認 pm2 已安裝：

```bash
which pm2 || npm install -g pm2
```

啟動服務：

```bash
cd ~/Development/<project-name>
pm2 start http-server --name "<project-name>" -- . -p <PORT>
pm2 save
```

驗證正在運行：

```bash
pm2 status
curl -s -o /dev/null -w "%{http_code}" http://localhost:<PORT>
```

確認回傳 200 才繼續。

---

## Step 7：Router Virtual Servers 設定

詳見 `references/router.md`。

設定完成後，回傳公共網址給使用者：

```
http://220.135.50.87:<PORT>
```

---

## Step 8：詢問是否推送至 GitHub（首次部署）

部署成功並回傳公共網址後，詢問使用者：

> 「部署完成！是否要將專案代碼推送至 GitHub 進行版本控制？」

### 若使用者回覆「是」：

**Step 8-1：確認 gh 登入狀態**

```bash
gh auth status
```

若未登入，提示使用者提供 Personal Access Token 並執行：

```bash
echo "<TOKEN>" | gh auth login --with-token
```

**Step 8-2：初始化 Git 並建立 GitHub Repo**

```bash
cd ~/Development/<project-name>
git init
git add .
git commit -m "Initial deployment"
```

使用 GitHub CLI 建立同名的 private repo：

> 注意：所有 repo 一律建立為 **private**，禁止建立 public repo。

```bash
gh repo create <project-name> --private --source=. --remote=origin --push
```

確認推送成功：

```bash
gh repo view <project-name> --web 2>/dev/null || echo "已建立 repo：https://github.com/$(gh api /user --jq .login)/<project-name>"
```

完成後告知使用者 repo 網址：

> 「已建立 GitHub Repo：`https://github.com/<username>/<project-name>`，代碼已成功推送。」

### 若使用者回覆「否」：

略過，流程結束。

---

## 修改需求處理

若使用者提出修改需求：

1. 使用 Claude Code 進行修改：
   ```bash
   cd ~/Development/<project-name>
   claude --permission-mode bypassPermissions --print '<需求描述>'
   ```
2. 重新執行 Step 4 測試
3. pm2 restart（無需重新設定 Virtual Servers，port 不變）：
   ```bash
   pm2 restart <project-name>
   ```
4. 回傳公共網址供確認
5. 將代碼變更推送至 GitHub（若已設定版本控制）：
   ```bash
   cd ~/Development/<project-name>
   git add .
   git commit -m "<需求描述的摘要>"
   git push origin main
   ```
   完成後告知使用者：「代碼已推送至 GitHub。」

---

## 移除專案

若使用者要將某個專案完整移除，**必須先取得使用者明確確認後才可執行任何刪除動作**。

### Step R0：向使用者確認刪除意圖

在執行任何刪除操作之前，先回覆使用者以下確認訊息（依實際專案名稱代入）：

> 確認要刪除專案 `<project-name>` 嗎？
> 此動作將會：
> - 停止並移除 pm2 服務（釋放 port `<PORT>`）
> - 移除 Router Virtual Server 設定
> - 永久刪除 `~/Development/<project-name>` 資料夾及所有內容
>
> **此動作不可復原，請確認後再繼續。**
> 請回覆「確定刪除」以繼續，或回覆「取消」以中止。

**等待使用者明確回覆「確定刪除」後，才開始執行以下步驟。**
若使用者回覆取消或任何非確認字詞，則中止流程並告知「已取消刪除操作」。

---

### Step R1：停止並移除 pm2 服務（釋放 port）

```bash
# 停止服務
pm2 stop <project-name>
# 從 pm2 清單中移除
pm2 delete <project-name>
pm2 save
```

驗證 port 已釋放：

```bash
ss -tlnp | grep <PORT>
# 若無輸出，代表 port 已成功釋放
```

### Step R2：移除 Router Virtual Server（全自動）

使用 agent-browser 自動登入路由器並刪除對應的 Virtual Server 設定。

**Step R2-1：登入路由器**

```bash
npx agent-browser open http://192.168.0.1/
npx agent-browser snapshot -i
# 找到密碼輸入框 ref，填入密碼並登入
npx agent-browser fill @<password-ref> "Aemass160220"
npx agent-browser click @<login-btn-ref>
npx agent-browser wait --load networkidle
```

**Step R2-2：切換 Advanced 模式並進入 Virtual Servers**

```bash
npx agent-browser find text "Advanced" click
npx agent-browser wait 1000
npx agent-browser snapshot -i
# 點擊 NAT Forwarding → Virtual Servers
npx agent-browser click @<nat-forwarding-ref>
npx agent-browser wait 500
npx agent-browser snapshot -i
npx agent-browser click @<virtual-servers-ref>
npx agent-browser wait --load networkidle
```

**Step R2-3：找到並刪除目標項目**

```bash
npx agent-browser snapshot -i
# 先嘗試從 accessibility tree 找到對應的刪除按鈕 ref 並點擊
# 若刪除按鈕不在 accessibility tree，使用 JavaScript：
npx agent-browser eval "
  const rows = document.querySelectorAll('table tr');
  for (const row of rows) {
    if (row.innerText.includes('<project-name>')) {
      const deleteBtn = row.querySelector('[id*=del], [name*=del], button');
      if (deleteBtn) { deleteBtn.click(); break; }
    }
  }
  'done'
"
npx agent-browser wait 1000
npx agent-browser snapshot -i
# 確認 <project-name> 項目已從清單中消失
```

### Step R3：刪除專案資料夾

```bash
rm -rf ~/Development/<project-name>
```

確認已移除：

```bash
ls ~/Development/
# 確認 <project-name> 已不存在於清單中
```

完成後告知使用者：「專案 `<project-name>` 已完整移除，port `<PORT>` 已釋放。」
