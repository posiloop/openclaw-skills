---
name: session-usage
description: Session 模型切換與用量追蹤助理。Use when the user wants to switch the current OpenClaw session model, check current session token/cost usage, or maintain a local usage ledger for later rollups like today/this week/this month spending. Trigger on requests such as「切到 gpt-5.4」,「改用便宜一點的模型」,「現在這個 session 用了多少 token」,「這週總共花多少」, or similar model/usage/cost questions.
---

# Session Usage

## Overview

用這個 skill 處理兩類事：

1. 切換目前 session 的 model override
2. 查詢並記錄目前 session 的 usage，之後可累積成日／週／月統計

優先使用 OpenClaw 一級工具：

- 切模型用 `session_status(model=...)`
- 查目前 session 狀態用 `session_status()`

不要繞 shell、不要自己發 provider API。

## 核心流程

### 1. 切換模型

當使用者要切模型時：

1. 解析使用者目標模型
2. 呼叫 `session_status(model=...)` 設定目前 session override
3. 回覆切換後的模型
4. 立刻把這次狀態寫進 usage ledger，至少記：時間、session、model、tokens、cost

如果使用者說「便宜一點」或「快一點」但沒指定模型：

- 先給 2 到 3 個選項與建議
- 不要假設一個不存在或未驗證可用的 model id
- 若環境已有明確預設模型，可用目前模型當對照說明

若要重設 override，使用 `session_status(model="default")`。

### 2. 查目前 session usage

當使用者問目前用了多少 token / 花多少錢：

1. 呼叫 `session_status()`
2. 擷取至少下列資訊：
   - model
   - session key
   - input tokens
   - output tokens
   - cost（若工具有提供）
3. 回覆精簡摘要
4. 同步把快照 append 到 ledger

### 3. 查累積成本或用量

當使用者問今天 / 本週 / 本月 / 某段期間花多少時：

1. 先讀 ledger（預設 `references/usage-ledger.jsonl`）
2. 依時間區間過濾
3. 依需求彙總：
   - 總成本
   - 總 input/output tokens
   - 依 model 分組
   - 依 session 分組（需要時）
4. 若 ledger 裡沒有 provider cost，就明確標示為 `unknown` 或 `estimated`，不要假裝精確

## Ledger 規格

預設 ledger 檔案：`references/usage-ledger.jsonl`

每行一筆 JSON，建議欄位：

```json
{
  "timestamp": "2026-04-24T19:12:12+08:00",
  "session": "agent:main:slack:channel:c0ajdqatejj:thread:1777024887.905599",
  "channel": "slack",
  "scope": "current_session_snapshot",
  "model": "openai-codex/gpt-5.4",
  "input_tokens": 21000,
  "output_tokens": 653,
  "total_tokens": 21653,
  "cost": null,
  "cost_source": "provider_missing",
  "note": "session_status snapshot"
}
```

規則：

- 只 append，不覆寫舊資料
- `cost` 若無資料，存 `null`
- `cost_source` 至少區分：`provider_reported`、`estimated`、`provider_missing`
- 同一次查詢如果已經寫過非常接近的重複快照，可接受，但避免無意義連續重複寫入

## 解析 `session_status` 的實務規則

`session_status` 通常可直接讀到：

- 模型名稱
- Tokens: `X in / Y out`
- Session key
- 可能的 cost / usage 資訊

處理原則：

- 先信任工具原生欄位
- 沒有 cost 就不要自行腦補
- 若未來要做估算，再依模型單價另行標註 `estimated`

## 建議回覆格式

### 切模型後

```text
已切到 openai-codex/gpt-5.4。
目前這個 session 已套用 model override，剛剛也幫你記到 usage log 了。
```

### 查目前 session

```text
目前 session：openai-codex/gpt-5.4
input tokens：21k
output tokens：653
cost：unknown（provider 沒回）
```

### 查區間彙總

```text
今天目前累計：
- cost：$1.23
- input tokens：120k
- output tokens：8.4k
- 主要模型：openai-codex/gpt-5.4
```

若 cost 不完整，要直接說：

```text
目前只能可靠統計 token。
cost 有些快照沒有 provider 回傳，所以總成本是部分資料，不是完整精算。
```

## 實作建議

- 若需要重複計算與彙總，新增腳本到 `scripts/`
- 腳本應優先負責 ledger append、JSONL 解析、區間彙總
- 新腳本要實跑測試

## Resources

### references/

- `usage-ledger.jsonl`: 本地 usage ledger，供後續日／週／月彙總
