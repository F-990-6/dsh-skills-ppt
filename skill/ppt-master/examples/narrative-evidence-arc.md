# Narrative Spine

- **Spine**: dsh-evidence-arc

## Slide 01 — hook

- **Beat**: hook
- **Title**: 校园活动，自动抵达
- **Claim**: 22 天里，它替你试了 547 次。
- **Source**: logs/抢活动.log，2026-10-08 至 2026-10-30，74,226 行

## Slide 02 — conflict

- **Beat**: conflict
- **Title**: 名额不等人
- **Relationships**: contrast between 手动一遍 30 秒 and 名额几秒被抢空
- **Claim**: 手动 30 秒，名额几秒；人不可能 24 小时盯屏。
- **Data class**: scenario — 30 秒与「几秒」是量级估计，非实测分布

## Slide 03 — method

- **Beat**: method
- **Title**: 四道工序，把请求送进开放那一秒
- **Mapping**: 对时 → 时钟误差；巡检 → 盯屏；并行 → 多活动；重试 → 空等
- **Source**: 源码 E:\服务号活动\fjtcm-GrabActivities.py，2026-10

## Slide 04 — evidence

- **Beat**: evidence
- **Title**: 22 天，它替你跑了这些
- **Claim**: 547 次登录、545 轮巡检、30 次报名确认、74,226 行日志。
- **Source**: logs/抢活动.log，74,226 行，2026-10-08 至 2026-10-30
- **Boundary**: 失败多为接口超时，不是抢不到；30 次不是「全中」，是能进的窗口里一次没漏。
