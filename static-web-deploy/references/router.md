# Router Virtual Servers 設定流程

## 基本資訊

- Router 後台：`http://192.168.0.1`
- 登入密碼：`Aemass160220`
- 操作工具：`npx agent-browser`

---

## 完整操作步驟

### 1. 開啟並登入

```bash
npx agent-browser open http://192.168.0.1/
npx agent-browser snapshot -i
# 找到密碼輸入框 ref (通常是唯一的 textbox)
npx agent-browser fill @<password-ref> "Aemass160220"
npx agent-browser click @<login-btn-ref>
npx agent-browser wait --load networkidle
```

### 2. 切換到 Advanced 模式

```bash
npx agent-browser find text "Advanced" click
npx agent-browser wait 1000
npx agent-browser snapshot -i
# 確認左側選單出現 "NAT Forwarding"
```

### 3. 進入 Virtual Servers

```bash
# 點擊 NAT Forwarding 展開子選單
npx agent-browser click @<nat-forwarding-ref>
npx agent-browser wait 500
npx agent-browser snapshot -i
# 點擊 Virtual Servers 子項目
npx agent-browser click @<virtual-servers-ref>
npx agent-browser wait --load networkidle
```

### 4. 新增 Virtual Server

> **注意：Add 按鈕不會出現在 accessibility tree，必須使用 JavaScript 點擊。**

```bash
# 使用 JavaScript 點擊 Add 按鈕（id="add"）
npx agent-browser eval "document.querySelector('#add').click(); 'clicked'"
npx agent-browser wait 1000
npx agent-browser snapshot -i
# 確認表單出現（應看到 Service Type、External Port 等 textbox）
```

填寫表單（依 snapshot 結果找到對應 ref）：

| 欄位 | 值 |
|------|-----|
| Service Type | `<project-name>` |
| External Port | `<PORT>` |
| Internal IP | 主機內部 IP 四個 octet 各自填入對應 textbox |
| Internal Port | `<PORT>` |
| Protocol | TCP（預設保持不變） |
| Enable This Entry | 勾選（預設通常已勾選） |

```bash
# Service Type
npx agent-browser fill @<service-type-ref> "<project-name>"
# External Port
npx agent-browser fill @<external-port-ref> "<PORT>"
# Internal IP（四個欄位分別對應四個 octet）
npx agent-browser fill @<ip-octet1-ref> "192"
npx agent-browser fill @<ip-octet2-ref> "168"
npx agent-browser fill @<ip-octet3-ref> "0"
npx agent-browser fill @<ip-octet4-ref> "108"
# Internal Port
npx agent-browser fill @<internal-port-ref> "<PORT>"
# Protocol 保持 TCP 預設值
# Enable This Entry 確認已勾選
```

### 5. 儲存

```bash
# 從 snapshot 找到 Save 按鈕 ref 後點擊
npx agent-browser click @<save-btn-ref>
npx agent-browser wait --load networkidle
npx agent-browser snapshot -i
# 確認新項目出現在清單中，含正確的 Service Type 與 Port
```

---

## 刪除 Virtual Server

### 1. 登入並進入 Virtual Servers 頁面

依照「完整操作步驟」的 Step 1～3 登入並導航至 Virtual Servers 頁面。

### 2. 找到並刪除目標項目

```bash
npx agent-browser snapshot -i
# 在清單中找到 Service Type 為 <project-name> 的項目
# 找到該列對應的「Delete」或「刪除」按鈕 ref
```

若刪除按鈕不在 accessibility tree，使用 JavaScript：

```bash
# 先用 snapshot 確認目標列的索引或唯一識別，再透過 eval 操作
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
```

或直接點擊找到的 ref：

```bash
npx agent-browser click @<delete-btn-ref>
npx agent-browser wait 1000
```

### 3. 確認刪除

```bash
npx agent-browser snapshot -i
# 確認 <project-name> 的項目已從清單中消失
```

---

## 注意事項

- 千萬不要修改其他已存在的 Virtual Servers 項目
- 每次操作後重新 snapshot 取得最新 ref，ref 在頁面導航後會改變
- 若 agent-browser 未安裝：`npx agent-browser --version` 會自動安裝
- 查詢主機 IP：`ip addr show | grep "inet " | grep -v 127.0.0.1`（若 `ifconfig` 不可用）
