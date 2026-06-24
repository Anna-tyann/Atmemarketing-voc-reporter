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
