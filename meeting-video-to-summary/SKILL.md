---
name: meeting-video-to-summary
description: 將會議影片自動轉成 Meeting Ink 風格的 AI 摘要，並直接寫入 Google Drive 指定資料夾。輸入為 Google Drive 分享連結（或本機影片路徑），會依序執行影片下載、音訊抽取、OpenAI whisper-1 逐字稿、依 Meeting Ink 固定模板（頁首 metadata + TODO / DONE / 其他相關資訊）產出摘要，最後將摘要上傳至 Google Drive 中的「Claude AI 會議記錄」資料夾成為獨立 Google 文件，回傳文件連結。當使用者提到「會議影片」、「會議錄影」、「整理會議紀錄」、「逐字稿 + 摘要」或貼上 Google Drive 會議連結時使用此 skill。
---

# Meeting Video to Summary

## Overview

把一支會議影片（Google Drive 連結或本機檔）自動轉成一份符合 Meeting Ink 格式的 AI 摘要，並上傳到 Google Drive 指定資料夾。

核心資料流：
```
Google Drive URL / local path
        ↓ gdown / cp
      video.mp4
        ↓ ffmpeg
      audio.mp3
        ↓ OpenAI whisper-1 (curl)
    transcript.txt
        ↓ Claude 讀取 + 依模板整理
      summary.md          (本地保留，供後續查驗)
        ↓ md2html.py
      summary.html
        ↓ mcp__claude_ai_Google_Drive__create_file
      Google Doc in「Claude AI 會議記錄」folder
        ↓
      回傳文件連結給使用者
```

## Triggers

當使用者：
- 貼出 Google Drive 影片連結並要求整理成會議紀錄
- 提供本機會議影片路徑並要求逐字稿 + 摘要
- 明確說「做會議紀錄」、「整理這場會議」、「會議 AI 摘要」

## Constants

- **目標資料夾 ID**：`13xYAAzoBC76l7EfnYX3j8G-H28bGUjSM`（Google Drive 中的「Claude AI 會議記錄」資料夾，由 Che An Wu 分享給 giintaipei@gmail.com）
- **目標資料夾連結**：https://drive.google.com/drive/folders/13xYAAzoBC76l7EfnYX3j8G-H28bGUjSM

若未來資料夾變動，請更新此段。

## Workflow

### 1. 釐清輸入（**必做**，不可跳過）

在呼叫 `run.sh` **之前**，必須向使用者確認以下資訊並取得回答：

- 影片來源（Google Drive 連結或本機路徑）
- 會議名稱（用來命名本地資料夾與 Google Doc 標題，例如「AICoach 進度會議」）
- 會議日期（若檔名或內容推得出，直接取用；推不出則問）
- **與會者名單（必填）**：逐字稿無 speaker diarization，若不問就只能靠語意推測，容易錯（例如把「韋丞」聽成「維成」、「智森」聽成「自身」）。請使用者用逗號分隔列出本次會議的實際與會者姓名。若使用者真的不清楚，才退為「待確認」。

問法範例：
> 開始前請給我這場會議的：
> 1. 會議名稱（例：AICoach 2.0 進度會議）
> 2. 會議日期（今天的話可不用給）
> 3. 與會者名單（逗號分隔，例：韋丞, Tina, 智森）

若 Google Drive 連結無法直接下載（需登入），請使用者改為公開分享（連結權限設為「知道連結者可檢視」），或手動下載後改給本機路徑。

### 2. 執行 pipeline（下載 + 抽音 + 轉逐字稿）

```bash
bash ${SKILL_DIR}/scripts/run.sh "<URL_OR_PATH>" "<會議名稱>"
```

本地輸出資料夾：`~/Desktop/meeting-records/YYYY-MM-DD_<會議名稱>/`

會產出：
- `video.mp4` — 原始影片
- `audio.mp3` — 抽取出的音訊（mono, 16kHz, mp3）
- `transcript.txt` — OpenAI whisper-1 逐字稿

### 3. Claude 讀取逐字稿並產出摘要

讀取 `transcript.txt`，依據 `references/summary-template.md` 填入內容，輸出到同一資料夾下的 `summary.md`（本地檔，供後續查驗或重新上傳）。

**摘要內容必須依照以下結構**（對應 Meeting Ink 模板）：

#### 頁首 metadata
- 會議標題
- 建立時間（今天日期）
- 音檔時長（從 pipeline 執行輸出的 duration 取得）
- 與會者：**使用步驟 1 使用者提供的名單原樣填入**，不要從逐字稿推測。逐字稿中若出現與名單相近但寫錯的字（例如「維成」vs「韋丞」、「自身」vs「智森」），視為語音辨識誤差，以使用者提供的名單為準。

#### TODO（待辦）
三個子分類，每類一個 markdown 表格，欄位：`預計完成時間 | 工作內容 | 負責人或窗口`
- 原定要完成的部分
- 新增加的部分
- 潛在要做但還沒規劃時間的部分

#### DONE（已完成 / 確認項目）
以「主題 → 狀態 → 延伸下一步」三段式呈現。

#### 其他相關資訊
依議題分成多個二級標題，每個標題下：一段情境說明 + 細項條列（多為「標籤：內容」鍵值形式）。

#### 頁尾
- Meeting Time（會議實際發生時間，若可推得）
- 免責聲明：「本會議紀錄摘要由 AI 自動產生，可能會有誤差，請以實際情況為主。」

### 4. 轉成 HTML

```bash
python3 ${SKILL_DIR}/scripts/md2html.py <OUTDIR>/summary.md <OUTDIR>/summary.html
```

### 5. 上傳到 Google Drive 資料夾

使用 `upload-gdoc.py`（基於 google-api-python-client + OAuth，會自動轉為 Google Doc）：

```bash
python3 ${SKILL_DIR}/scripts/upload-gdoc.py \
  "<OUTDIR>/summary.md" \
  "13xYAAzoBC76l7EfnYX3j8G-H28bGUjSM" \
  "YYYY-MM-DD 會議標題"
```

- 第一個參數：要上傳的本地檔（.md / .html / .txt 皆可）
- 第二個參數：目標資料夾 ID
- 第三個參數：Google Doc 標題
- stdout 會印出最終 Google Doc 的 webViewLink

OAuth credentials 位於 `~/.config/google-oauth/credentials.json`，首次授權後 token 快取於 `~/.config/google-oauth/token.json`，之後無需再授權。

**不要使用 `mcp__claude_ai_Google_Drive__create_file`**：該工具的 `content` 參數對超過 ~2KB 的 base64 會失敗，且不會把 text/html 轉成 Google Doc。

### 6. 回報結果

回覆使用者以下資訊：
- **Google Doc 連結**（從 `viewUrl` 取得）← 最重要
- 本地資料夾路徑（備份用）
- 音檔時長、逐字稿字數
- 若有模糊或不確定的項目（人名、日期、責任歸屬），用列表方式請使用者確認

## Rules

- **不要捏造內容**：摘要內容必須源自逐字稿。逐字稿中沒有明確資訊的欄位，標註「待確認」。
- **與會者名單必須由使用者提供**：不要從逐字稿推測人名。逐字稿中出現的人名若拼字與使用者提供的名單不一致（ASR 誤差），一律以使用者提供的名單為準，並在摘要其他段落提到此人時換用正確寫法。
- **不要略過流程**：即使影片很短，也必須走完完整 pipeline，保留中間產物方便後續查驗。
- **同名本地資料夾處理**：run.sh 已自動加時間戳避免覆蓋。
- **Google Doc 標題格式固定**：`YYYY-MM-DD 會議標題`（日期在前、空格、標題），不要加冒號、括號、斜線等特殊字元。
- **同名 Google Doc**：資料夾內允許同名，不做去重，讓每次執行都建立新版本。
- **逐字稿引擎**：OpenAI `whisper-1`，language=`zh`，response_format=`text`。OPENAI_API_KEY 從環境變數讀，讀不到時 fallback 至 `~/.config/openai/api_key`。要換模型可設 `TRANSCRIBE_MODEL=<name>`（例如 `gpt-4o-transcribe`），但 2026-04 實測 gpt-4o-transcribe 對 >8 分鐘的中文會議錄音會截斷輸出、會產生簡體、會幻覺，除非有特殊需求否則維持預設即可。
- **音訊檔大小**：OpenAI transcriptions API 上限 25MB。pipeline 已在超限時 fail fast；若被擋下需降低 bitrate 或切分音檔。whisper-1 本身沒有時長限制，25MB 以 40kbps mono 換算約 85 分鐘。

## Dependencies

- `gdown` — `/home/aemass/.local/bin/gdown`
- `ffmpeg` / `ffprobe` — `/home/linuxbrew/.linuxbrew/bin/ffmpeg`
- `curl` — 呼叫 OpenAI transcriptions API（API key 存於 `~/.config/openai/api_key`，600 權限）
- `python3` + `markdown`（HTML 轉換，可選，若要走 HTML 路徑才需要）
- `python3` + `google-api-python-client` / `google-auth-oauthlib`（上傳 Google Doc）
- OAuth credentials：`~/.config/google-oauth/credentials.json`（Desktop app 型 OAuth client）
- OAuth token：`~/.config/google-oauth/token.json`（首次授權後自動建立）

## References

- `references/summary-template.md` — Meeting Ink 摘要格式完整模板
- `scripts/run.sh` — pipeline 主腳本（video → transcript）
- `scripts/md2html.py` — markdown → HTML 轉換器（帶 table 支援）
