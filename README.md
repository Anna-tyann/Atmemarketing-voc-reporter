# 📊 Atmemarketing VOC Reporter

> 18维打标数据 → 交互式 HTML 洞察报告（含营销战略总结）

接收 `atmemarketing-voc-tagger` 产出的打标 JSON，一键生成包含散点图、柱状图、痛点卡片、用户画像、使用场景、产品建议和**营销战略方向总结**（社媒内容+网红合作+网站优化+投放人群包）的完整 HTML 报告。


---

## 🚀 快速开始

### 安装

```bash
git clone git@github.com:Anna-tyann/atmemarketing-voc-reporter.git
cd atmemarketing-voc-reporter
pip install pandas openpyxl

# 安装 Skill
cp -r skills/atmemarketing-voc-reporter ~/.claude/skills/
```

### 使用

**Claude Code Skill：**
```
/atmemarketing-voc-reporter
→ 提供打标 JSON 路径，自动生成 HTML 报告
```

**Python 直接调用：**
```python
from voc_engine import build_report_html
import json

with open('产品名_打标完成版.json') as f:
    tags_data = json.load(f)

html = build_report_html(tags_data, {'product_name': '产品名'})
with open('报告.html', 'w') as f: f.write(html)
```

---

## 📋 报告板块（11个）

| # | 板块 | 类型 |
|---|------|------|
| 1 | 📋 核心发现摘要 | 文本 |
| 2 | 📊 标签全景散点图 | ECharts 散点图 |
| 3 | 📈 一级标签情感分布 | ECharts 堆叠柱状图 |
| 4 | 🔍 一级标签散点图 | ECharts 散点图 |
| 5 | 🚨 核心用户痛点 | 洞察卡片+原文引用 |
| 6 | ✅ 产品核心优势 | 洞察卡片+原文引用 |
| 7 | 👥 目标用户画像 | 用户画像卡片 |
| 8 | 🎯 核心使用场景 | 场景卡片 |
| 9 | 💡 产品改进建议 | 建议卡片（优先级徽章） |
| 10 | 📑 附录：标签明细表 | 数据表 |
| 11 | 📌 营销战略方向总结 | 四大营销方向 |

---

## 📁 文件结构

```
atmemarketing-voc-reporter/
├── README.md
├── voc_engine.py                          # 核心引擎
├── skills/
│   └── atmemarketing-voc-reporter/
│       ├── SKILL.md                       # Skill 入口
│       └── references/
│           └── voc_engine.py              # 引擎副本
└── docs/
    ├── QUICKSTART.md
    └── METHODOLOGY.md
```

---

## 🔗 配套 Skill

- 打标 Skill: [atmemarketing-voc-tagger](https://github.com/Anna-tyann/atmemarketing-voc-tagger)
---

## 📄 License

MIT © Atmemarketing
---

## 🏢 关于 艾特密 / About @me

**艾特密（Atme Marketing）** 是一家专注跨境品牌增长的海外营销陪跑咨询机构。

我们不只出策略——更以 **"陪跑搭档"** 的角色，与品牌并肩走完从市场验证、策略制定到执行落地的每一步。

- 🕐 **10+ 年**跨境营销实战经验
- 🌍 覆盖 **20+ 国家**市场（北美、欧洲、东南亚、中东）
- 🏭 服务 **18+ 品牌**，覆盖 10+ 行业
- ⭐ **97%** 客户满意度
>
> **@me (Atme Marketing)** — Your cross-border brand growth partner. 10+ years experience across 20+ countries, 18+ brands served. We don't just strategize — we run the race with you.
>
>## 🛠️ 我们提供的服务

| 层级 | 服务 | 适合 |
|------|------|------|
| Step 1 | 海外销量机会情报包 | 正在评估海外机会的企业 |
| Step 2 | 1小时海外增长轻咨询 | 已出海但流量遇瓶颈的企业 |
| Step 3 | 海外增长实战训练营 | 需要系统提升团队能力的企业 |
| Step 4 | 基础陪跑 | 需要专业引导的品牌团队 |
| Step 5 | 深度陪跑 | 寻求全面增长体系搭建的品牌 |

>## 📮 找到我 / Get in Touch

- 💼 **公众号/视频号**：Anna跨境出海营销
- 📍 **地址**：深圳坂田
- 📱 **微信**：ianna666
- 📧 **邮箱**：[anna@atmemarketing.com](mailto:anna@atmemarketing.com)

*联系获取出海洞察 & 合作咨询*


> **全球视角起步，品牌战略落地**
> *"选择艾特密，不只是获得营销服务，更是找到一位共同成长的搭档，陪伴你从 0 到 1 搭建属于自己的海外增长引擎。"*
> *From Zero to One: Your Growth Partner for Global Markets*
> *Choosing @me isn't just hiring a marketing service — it's finding a partner who grows with you, helping you build your own overseas growth engine from scratch.*
