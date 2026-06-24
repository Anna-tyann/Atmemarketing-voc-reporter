# 🚀 5分钟快速上手

## 准备工作

```bash
pip install pandas openpyxl
```

确保你的评论数据 Excel 包含以下列：
- `rid` — 评论ID
- `title` — 评论标题
- `content` — 评论正文
- `rating` — 评分 (1-5)

可选但推荐：`asin`, `date`, `author`

---

## 方式一：Claude Code Skill（推荐）

### 安装 Skill

```bash
cp -r skills/atmemarketing-voc-tagger ~/.claude/skills/
cp -r skills/atmemarketing-voc-reporter ~/.claude/skills/
```

### 使用

在 Claude Code 对话中：

**Step 1 — 打标：**
```
/atmemarketing-voc-tagger
→ 告诉它你的 Excel 文件路径和产品名称
→ 自动生成「产品名_打标完成版.xlsx」
```

**Step 2 — 报告：**
```
/atmemarketing-voc-reporter
→ Skill 会自动加载上一步的 JSON
→ 生成「产品名_VOC分析报告.html」
→ 双击在浏览器中打开
```

---

## 方式二：直接调用 Python 引擎

### 冲牙器品类（使用内置标签体系）

```python
from voc_engine import tag_and_export, build_report_html, get_default_tag_system

# Step 1: 打标
tags_data, xlsx_path = tag_and_export(
    'waterpik_reviews.xlsx',
    get_default_tag_system(),
    'Waterpik 冲牙器'
)

# Step 2: 生成报告
html = build_report_html(tags_data, {
    'product_name': 'Waterpik 冲牙器',
    'tag_system': get_default_tag_system(),
})
with open('Waterpik_VOC报告.html', 'w', encoding='utf-8') as f:
    f.write(html)
```

### 其他品类（自定义标签体系）

```python
from voc_engine import extract_tags, build_report_html, load_excel

# 构建你的标签体系
my_tag_system = {
    "核心功能": {
        "color": "#2563eb",
        "l2": {
            "清洁效果": {"match": ["clean", "cleaning", "effective", ...]},
            "除味效果": {"match": ["smell", "odor", "fresh", ...]},
        }
    },
    # ... 更多 L1 类目
}

# 打标
df, preview = load_excel('your_data.xlsx')
tags_data = extract_tags(df, my_tag_system, 'Your Product')

# 生成报告
html = build_report_html(tags_data, {'product_name': 'Your Product', 'tag_system': my_tag_system})
with open('report.html', 'w') as f: f.write(html)
```

> 💡 行为场景维度（购买动因、使用地点、用户画像等8个）会自动合并到标签体系中，无需手动配置。

---

## 输出文件说明

### 打标完成版 Excel（4个Sheet）

| Sheet | 内容 |
|-------|------|
| 打标数据 | 原始列 + 标签数量、正面标签、负面标签、标签明细 |
| L1统计 | 一级类目汇总（标签数、正面率） |
| L2详情 | 二级标签明细（提及次数、正负面） |
| 洞察汇总 | 痛点/优势列表（含原文引用） |

### 分析报告 HTML（11个板块）

包含散点图、柱状图、痛点卡片、用户画像、营销战略建议等。单文件，可发送给任何人。

---

## 常见问题

**Q: 正面率和评分不一致怎么办？**
检查标签体系中的关键词——负面关键词过多会导致错判。减少通用负面词，增加正面词。

**Q: 标签太少（<1条/评论）？**
增加每个 L2 的关键词数量，降低匹配门槛。

**Q: 支持中文评论吗？**
引擎目前针对英文关键词优化。中文评论需要将关键词改为中文。
