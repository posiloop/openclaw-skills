# 黑名單與特徵檔案格式

## blacklist.json — 寄件者黑名單

```json
{
  "version": "1.0",
  "senders": [
    "noreply@spam-company.com",
    "@unwanted-domain.com"
  ],
  "sender_patterns": [
    ".*@newsletter\\..*",
    "no-reply@.*\\.marketing\\..*"
  ]
}
```

欄位說明：
- `senders`：完整 email 地址或 `@domain.com` 格式（匹配整個網域）
- `sender_patterns`：正則表達式，匹配寄件者

---

## spam_features.json — 垃圾郵件特徵

```json
{
  "version": "1.0",
  "subject_keywords": [
    "限時優惠",
    "免費領取",
    "恭喜您中獎"
  ],
  "subject_patterns": [
    ".*\\d+%\\s*折扣.*",
    ".*urgent.*action required.*"
  ],
  "body_keywords": [
    "unsubscribe",
    "click here to claim"
  ],
  "combined_rules": [
    {
      "description": "促銷郵件",
      "subject_contains_any": ["優惠", "折扣", "免費"],
      "sender_domain_not_in": ["trusted-shop.com"]
    }
  ]
}
```

欄位說明：
- `subject_keywords`：主旨包含任一關鍵字即視為垃圾郵件
- `subject_patterns`：主旨正則表達式
- `body_keywords`：郵件內文關鍵字（掃描前 500 字元）
- `combined_rules`：複合規則，可設定 AND/NOT 條件
