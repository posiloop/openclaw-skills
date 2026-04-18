---
name: pdf-knowledge-intake
description: Intake, organize, and summarize PDFs into a reusable local knowledge base with consistent markdown records and an index. Use when the user sends one or more PDFs and wants them identified, summarized, added to a knowledge repository, or checked against an existing knowledge index before storing.
---

# PDF Knowledge Intake

## Goal

Handle incoming PDF documents as knowledge assets, not just one-off chat attachments. Read each PDF, identify the topic, ask whether it should be stored in the knowledge base, then create searchable markdown files plus an index entry.

## Triggering rules

Use this skill when the user does one or more of the following:

- sends one or more PDF or document files
- mentions PDF, 文件, 簡報, 白皮書, 提案書, 招商簡報, 或知識庫
- asks to read, summarize, 整理, 入庫, 建知識庫, 建索引, or compare against existing stored materials
- asks for one batch report after several PDFs are finished instead of interrupting between files

Treat these as strong triggers even when the user does not explicitly say "建知識庫":

- "幫我看這份 PDF"
- "這個好像是在講某個品牌或產品"
- "整理一下這批簡報"
- "把這些文件入庫"

## Core behavior

### When the user only throws PDFs without clear purpose

Default to this conversation rhythm:

1. confirm receipt
2. identify the likely topic
3. ask whether to add it into the knowledge base

Use short prompts like:

- 「我收到這份 PDF，看起來是在講星鏈咖啡機的招商模式。要不要我直接把它整理進知識庫？」
- 「這份像是品牌提案簡報，要我幫你入知識庫嗎？」

### When the user explicitly asks to read and report later

Read the whole batch first, then reply once after all requested PDFs are processed. Do not interrupt mid-batch unless a blocker appears.

### When the user wants knowledge-base intake

Follow this sequence:

1. read the PDF content and extract what is actually visible
2. identify document type and main subject
3. read `references/knowledge-index.md` before creating new entries when deduplication or naming conflicts are possible
4. create or update `references/knowledge/<slug>.md`
5. update `references/knowledge-index.md`
6. reply with a compact summary and whether the item was added

If text extraction is incomplete, say so clearly. Do not pretend to have read missing pages or unreadable sections.

## Writing rules

- Do not pretend to have read content that was not actually available.
- If the main text cannot be captured, explicitly say what source was available instead.
- Allow an initial draft summary, but record uncertainty in `Notes`.
- Prioritize searchability, reusability, and extendability over chat-style prose.
- When the user sends many PDFs at once, organize them one by one but keep the markdown structure consistent.
- When the user asks for one combined readout after all PDFs are finished, complete the batch before reporting.

## Knowledge base files

Use these local files:

- `references/knowledge-index.md`
- `references/knowledge/*.md`

Read the index first when needed to avoid duplicate intake or naming collisions.

## Index maintenance

Every entry in `references/knowledge-index.md` should record:

- slug
- title
- type
- topic
- tags
- one-sentence summary

Use a simple bullet format that is easy to scan and diff.

## Knowledge entry format

Use this template for `references/knowledge/<slug>.md`:

```md
# <標題>

## Metadata

- 類型：
- 來源：
- 狀態：已入庫
- 標籤：

## Summary

一句話摘要。

## Core Positioning

文件的核心定位、主張或目的。

## Key Points

- 重點 1
- 重點 2
- 重點 3

## Read Details

- 已讀到的細節 1
- 已讀到的細節 2
- 已讀到的細節 3

## Scenarios

- 適用場景 1
- 適用場景 2

## Notes

- 不確定、假設、待補資訊
```

## Readout format after reading a PDF

For each PDF, provide a compact report with:

1. what the document appears to be about, in 3 to 8 short lines
2. the fields that are currently identifiable, such as:
   - brand name
   - product name
   - specifications
   - pricing
   -加盟方式
   -分潤或回本資訊
   -維運模式
   -目標場景
3. explicit uncertainty when the image or PDF is incomplete
4. whether it was added to the knowledge base

## Current seed example

Include entries like this in the index when relevant:

- `starchain-coffee-machine`: 星鏈咖啡機｜招商簡報｜AI 咖啡機、加盟、無人零售｜星鏈咖啡機加盟與 AI 營運模式提案
