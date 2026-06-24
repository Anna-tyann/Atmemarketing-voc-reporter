---
name: atmemarketing-voc-reporter
version: 2.0.0
description: >-
  Atmemarketing VOC 报告生成工具。接收18维打标 JSON 数据，生成包含散点图、情感分布柱状图、
  用户痛点深度解读、产品优势、用户画像、使用场景、改进建议、以及营销战略方向总结
  （社媒内容策略+网红合作+网站优化+投放人群包）的完整 HTML 交互式报告（ECharts）。
  标签明细表在附录，营销战略总结在最后。单文件，双击浏览器打开。
metadata:
  author: Atmemarketing
  category: VOC分析
  requires:
    bins: ["python3"]
    libs: ["pandas"]
  pipeline_stage: 2
  input: 打标完成版.json
  output: 产品名_VOC分析报告.html
  homepage: https://github.com/atmemarketing/atmemarketing-voc
---

# Atmemarketing VOC 报告生成 Skill

## 概述

接收 18维打标 JSON → 生成完整 HTML 交互式报告。单文件，双击浏览器打开。

---

## 报告板块（11个，按顺序）

| # | 板块 | 内容 |
|---|------|------|
| 1 | 📋 核心发现摘要 | 数据总览+行为维度亮点 |
| 2 | 📊 标签全景散点图 | L2标签：提及×正面率（ECharts） |
| 3 | 📈 一级标签情感分布 | 正面/负面/中性堆叠柱状图 |
| 4 | 🔍 一级标签散点图 | 关注度×满意度+参考线 |
| 5 | 🚨 核心用户痛点 | 痛点卡片+原文引用 |
| 6 | ✅ 产品核心优势 | 优势卡片+原文引用 |
| 7 | 👥 目标用户画像 | 用户画像卡片 |
| 8 | 🎯 核心使用场景 | 场景卡片 |
| 9 | 💡 产品改进建议 | 建议卡片（优先级徽章） |
| 10 | 📑 附录：标签明细表 | 完整L1→L2数据表 |
| 11 | 📌 营销战略方向总结 | 四大方向：社媒+网红+网站+投放 |

---

## 执行流程

### Step 1: 获取打标数据

```python
import json
with open('产品名_打标完成版.json', 'r') as f:
    tags_data = json.load(f)
```

### Step 2: 优化洞察内容（可选）

检查 `tags_data` 中的 personas、scenarios、recommendations 是否需要手动调整。打标 Skill 自动生成的洞察可作为起点，手动优化后报告质量更高。

### Step 3: 生成报告

```python
import sys
sys.path.insert(0, 'voc_engine.py所在目录')
from voc_engine import build_report_html

product_config = {'product_name': '产品名称', 'tag_system': tag_system}
report_html = build_report_html(tags_data, product_config)

with open('产品名_VOC分析报告.html', 'w', encoding='utf-8') as f:
    f.write(report_html)
```

### Step 4: 预览

```bash
open 产品名_VOC分析报告.html  # macOS
# 或双击 HTML 文件
```

---

## 营销战略方向总结（板块11）

报告最后板块，基于行为维度标签自动生成四大营销方向：

### 🎬 社媒内容策略
- 「真实对比」型：用户从竞品转向本产品的故事
- 「使用场景」型：浴室、旅行、户外等真实场景
- 「用户证言」型：高情感密度用户故事

### 🤝 海外网红合作方向
基于用户兴趣维度筛选四类网红：口腔健康KOL、科技数码博主、旅行户外博主、家庭亲子博主

### 🌐 网站与落地页优化
基于使用地点维度确定 Hero 区视觉、quote轮播、信任徽章

### 🎯 精准投放人群包
用户画像×购买动因×兴趣 三维交叉，四组人群差异化素材

---

## 设计规范

- 颜色：正面 `#22c55e`｜负面 `#ef4444`｜Header 渐变 `#1e3a5f→#2563eb→#7c3aed`
- 散点图：50%满意度参考线 + 高关注度参考线
- 痛点卡片红色左边框，优势绿色左边框
- 移动端（<768px）自动单列

---

## 引擎文件位置

`voc_engine.py` 查找顺序同打标 Skill。

---

## 注意事项

- 报告是单文件，ECharts 从 CDN 加载（需网络）
- 洞察质量 > 数量
- 所有痛点/优势必须附带原文 quote
- 界面中文，原文保留原始语言
