---
name: static-web-deploy
description: 部署靜態網頁（HTML/CSS/JavaScript）到本機伺服器並對外開放訪問。當使用者上傳 HTML、CSS、JS 等靜態網頁檔案並說要「部署」、「上線」、「發布」時使用此 skill。亦支援移除專案，包含停止 pm2 服務釋放 port、移除 router Virtual Server、刪除專案資料夾。流程包含：建立專案資料夾、啟動 http-server 測試、Claude Code bug 修復、pm2 背景運行、設定 router Virtual Servers 對外開放，最後回傳公共網址供使用者確認。部署成功後詢問是否推送至 GitHub 進行版本控制（首次部署建立 repo、後續修改 push 更新）。
---

# Static Web Deploy

## 整體流程

1. 詢問專案名稱 → 建立專案資料夾
2. 複製網頁檔案
3. http-server 測試
4. (如有錯誤) Claude Code 修復
5. pm2 背景運行
6. Router Virtual Servers 設定
7. 回傳公共網址
8. 詢問是否推送至 GitHub（首次部署建立 repo；修改需求則 push 更新）

詳細步驟請參閱 `references/workflow.md`。
路由器操作步驟請參閱 `references/router.md`。
