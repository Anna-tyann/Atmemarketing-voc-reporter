#!/usr/bin/env python3
"""
VOC 报告生成器 - 更新版
基于 EBO 更新版报告的模板
"""
import pandas as pd
import json

def generate_voc_report(excel_path, output_path=None):
    """
    从打标 Excel 生成完整的 HTML 报告

    Args:
        excel_path: 打标完成版 Excel 路径
        output_path: 输出 HTML 路径（默认自动生成）

    Returns:
        output_path: 生成的报告路径
    """

    # 1. 读取数据
    df_tags = pd.read_excel(excel_path, sheet_name='打标数据')
    df_l1 = pd.read_excel(excel_path, sheet_name='L1统计')
    df_l2 = pd.read_excel(excel_path, sheet_name='L2详情')

    # 2. 构建 meta 数据
    meta = {
        'total_reviews': len(df_tags),
        'total_tags': int(df_tags['标签数量'].sum()),
        'avg_rating': float(df_tags['rating'].mean()),
        'total_positive': int(df_tags['正面标签'].sum()),
        'total_negative': int(df_tags['负面标签'].sum()),
        'total_neutral': int(df_tags['中性标签'].sum()),
    }

    total = meta['total_positive'] + meta['total_negative'] + meta['total_neutral']
    meta['positive_rate'] = round(meta['total_positive'] / total * 100, 1) if total > 0 else 0
    meta['negative_rate'] = round(meta['total_negative'] / total * 100, 1) if total > 0 else 0

    # 3. 提取痛点
    pain_points = []
    for _, row in df_l2.iterrows():
        total_count = int(row['出现次数'])
        neg_count = int(row['负面'])
        pos_count = int(row['正面'])

        if total_count >= 10 and neg_count > pos_count:
            # 提取评论
            sample_reviews = df_tags[
                (df_tags['标签明细'].str.contains(str(row['L2']), na=False)) &
                (df_tags['rating'] <= 3)
            ].head(2)

            quotes = []
            for _, review in sample_reviews.iterrows():
                quotes.append({
                    'text': str(review['content'])[:150],
                    'rating': int(review['rating'])
                })

            pain_points.append({
                'category': row['L1'],
                'issue': row['L2'],
                'count': total_count,
                'negative_count': neg_count,
                'quotes': quotes
            })

    pain_points = sorted(pain_points, key=lambda x: x['negative_count'], reverse=True)[:10]

    # 4. 提取优势
    strengths = []
    for _, row in df_l2.iterrows():
        total_count = int(row['出现次数'])
        pos_count = int(row['正面'])
        pos_rate = pos_count / total_count if total_count > 0 else 0

        if total_count >= 10 and pos_rate >= 0.75:
            sample_reviews = df_tags[
                (df_tags['标签明细'].str.contains(str(row['L2']), na=False)) &
                (df_tags['rating'] >= 4)
            ].head(2)

            quotes = []
            for _, review in sample_reviews.iterrows():
                quotes.append({
                    'text': str(review['content'])[:150],
                    'rating': int(review['rating'])
                })

            strengths.append({
                'category': row['L1'],
                'strength': row['L2'],
                'count': total_count,
                'positive_rate': pos_rate,
                'quotes': quotes
            })

    strengths = sorted(strengths, key=lambda x: x['count'], reverse=True)[:12]

    # 5. 用户画像
    personas = []
    for _, row in df_l2.iterrows():
        if '用户' in str(row['L1']):
            personas.append({
                'type': f"{row['L1'].replace('👤 ', '').replace('👥 ', '').replace('🎓 ', '')}: {row['L2']}",
                'percentage': f"{int(row['出现次数']) / len(df_tags) * 100:.1f}%",
                'count': int(row['出现次数'])
            })
    personas = sorted(personas, key=lambda x: x['count'], reverse=True)[:8]

    # 6. 核心场景
    scenarios = []
    for _, row in df_l2.iterrows():
        if '场景' in str(row['L1']):
            pos_rate = int(row['正面']) / int(row['出现次数']) if int(row['出现次数']) > 0 else 0
            scenarios.append({
                'scenario': f"{row['L1'].replace('📍 ', '').replace('⏰ ', '').replace('🎯 ', '').replace('🌤️ ', '')}: {row['L2']}",
                'count': int(row['出现次数']),
                'satisfaction': f"{pos_rate*100:.1f}%"
            })
    scenarios = sorted(scenarios, key=lambda x: x['count'], reverse=True)[:10]

    # 7. 改进建议
    recommendations = []
    for i, pain in enumerate(pain_points, 1):
        priority = "高" if i <= 3 else ("中" if i <= 6 else "低")
        recommendations.append({
            'title': f"改进 {pain['issue']}",
            'description': f"{pain['category']} | {pain['count']} 次提及，{pain['negative_count']} 次负面",
            'priority': priority
        })

    # 8. 生成 HTML
    html = generate_html_template(meta, df_l1, df_l2, pain_points, strengths, personas, scenarios, recommendations)

    # 9. 保存
    if output_path is None:
        import os
        base_name = os.path.basename(excel_path).replace('打标.xlsx', 'VOC分析报告.html')
        output_path = excel_path.replace(os.path.basename(excel_path), base_name)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_path


def generate_html_template(meta, df_l1, df_l2, pain_points, strengths, personas, scenarios, recommendations):
    """生成 HTML 模板"""

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VOC 分析报告</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
               background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
               padding: 20px; color: #333; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}

        .header {{ background: white; border-radius: 12px; padding: 40px;
                  margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header h1 {{ color: #667eea; font-size: 36px; margin-bottom: 15px; }}
        .header .subtitle {{ color: #666; font-size: 18px; }}

        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px; margin-bottom: 20px; }}
        .kpi-card {{ background: white; border-radius: 12px; padding: 30px; text-align: center;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.3s; }}
        .kpi-card:hover {{ transform: translateY(-5px); }}
        .kpi-number {{ font-size: 48px; font-weight: bold; color: #667eea; margin-bottom: 10px; }}
        .kpi-label {{ color: #666; font-size: 16px; }}

        .section {{ background: white; border-radius: 12px; padding: 30px;
                   margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .section-title {{ font-size: 24px; font-weight: bold; color: #333;
                         margin-bottom: 20px; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}

        .chart {{ width: 100%; height: 500px; margin: 20px 0; }}

        .card-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                     gap: 20px; margin: 20px 0; }}
        .card {{ background: #f8f9fa; border-radius: 8px; padding: 20px;
                border-left: 4px solid #667eea; transition: transform 0.3s; }}
        .card:hover {{ transform: translateX(5px); }}
        .card.pain {{ border-left-color: #ef4444; }}
        .card.strength {{ border-left-color: #22c55e; }}
        .card-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #333; }}
        .card-count {{ color: #666; font-size: 14px; margin-bottom: 10px; }}
        .card-quote {{ background: white; padding: 15px; border-radius: 4px; margin-top: 10px;
                      font-style: italic; color: #555; font-size: 14px;
                      border-left: 3px solid #ffc107; }}
        .card-rating {{ color: #ffc107; margin-top: 5px; font-style: normal; }}

        .priority-high {{ color: #ef4444; font-weight: bold; }}
        .priority-mid {{ color: #f59e0b; font-weight: bold; }}
        .priority-low {{ color: #10b981; font-weight: bold; }}

        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #333; }}
        tr:hover {{ background: #f8f9fa; }}

        @media (max-width: 768px) {{
            .kpi-grid, .card-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📊 VOC 分析报告</h1>
        <p class="subtitle">基于 {meta['total_reviews']} 条真实用户评论的深度洞察</p>
    </div>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-number">{meta['total_reviews']}</div>
            <div class="kpi-label">总评论数</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-number">{meta['total_tags']}</div>
            <div class="kpi-label">总标签数</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-number">{meta['avg_rating']:.2f}</div>
            <div class="kpi-label">平均评分</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-number" style="color: #22c55e">{meta['positive_rate']}%</div>
            <div class="kpi-label">整体正面率</div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">📈 一级标签情感分布</div>
        <div id="chart_l1_bar" class="chart"></div>
    </div>

    <div class="section">
        <div class="section-title">🔍 一级标签分析：关注度 × 满意度</div>
        <div id="chart_l1_scatter" class="chart"></div>
    </div>

    <div class="section">
        <div class="section-title">🚨 核心用户痛点</div>
        <div class="card-grid">
'''

    # 添加痛点
    for i, pain in enumerate(pain_points, 1):
        quotes_html = ""
        for quote in pain.get('quotes', []):
            stars = "★" * quote['rating']
            quotes_html += f'<div class="card-quote">{quote["text"]}...<div class="card-rating">{stars}</div></div>'

        html += f'''
            <div class="card pain">
                <div class="card-title">{i}. {pain['issue']}</div>
                <div class="card-count">{pain['category']} | 提及 {pain['count']} 次，负面 {pain['negative_count']} 次</div>
                {quotes_html}
            </div>
        '''

    html += '''
        </div>
    </div>

    <div class="section">
        <div class="section-title">✅ 产品核心优势</div>
        <div class="card-grid">
'''

    # 添加优势
    for i, strength in enumerate(strengths, 1):
        quotes_html = ""
        for quote in strength.get('quotes', []):
            stars = "★" * quote['rating']
            quotes_html += f'<div class="card-quote">{quote["text"]}...<div class="card-rating">{stars}</div></div>'

        html += f'''
            <div class="card strength">
                <div class="card-title">{i}. {strength['strength']}</div>
                <div class="card-count">{strength['category']} | 提及 {strength['count']} 次，正面率 {strength['positive_rate']*100:.1f}%</div>
                {quotes_html}
            </div>
        '''

    html += '''
        </div>
    </div>

    <div class="section">
        <div class="section-title">👥 目标用户画像</div>
        <div class="card-grid">
'''

    for persona in personas:
        html += f'''
            <div class="card">
                <div class="card-title">{persona['type']}</div>
                <div class="card-count">占比：{persona['percentage']} ({persona['count']} 次提及)</div>
            </div>
        '''

    html += '''
        </div>
    </div>

    <div class="section">
        <div class="section-title">🎯 核心使用场景</div>
        <div class="card-grid">
'''

    for scenario in scenarios:
        html += f'''
            <div class="card">
                <div class="card-title">{scenario['scenario']}</div>
                <div class="card-count">提及 {scenario['count']} 次 | 满意度 {scenario['satisfaction']}</div>
            </div>
        '''

    html += '''
        </div>
    </div>

    <div class="section">
        <div class="section-title">💡 产品改进建议</div>
        <div class="card-grid">
'''

    for rec in recommendations:
        priority_class = 'priority-high' if rec['priority'] == '高' else ('priority-mid' if rec['priority'] == '中' else 'priority-low')
        html += f'''
            <div class="card">
                <div class="card-title"><span class="{priority_class}">[{rec['priority']}]</span> {rec['title']}</div>
                <div class="card-count">{rec['description']}</div>
            </div>
        '''

    html += '''
        </div>
    </div>

    <div class="section">
        <div class="section-title">📑 附录：标签明细</div>
        <table>
            <thead>
                <tr>
                    <th>排名</th>
                    <th>一级类目</th>
                    <th>标签总数</th>
                    <th>正面</th>
                    <th>负面</th>
                    <th>中性</th>
                    <th>正面率</th>
                </tr>
            </thead>
            <tbody>
'''

    for i, (_, row) in enumerate(df_l1.head(20).iterrows(), 1):
        html += f'''
                <tr>
                    <td><strong>{i}</strong></td>
                    <td>{row['一级类目']}</td>
                    <td>{int(row['标签总数'])}</td>
                    <td style="color: #22c55e"><strong>{int(row['正面'])}</strong></td>
                    <td style="color: #ef4444"><strong>{int(row['负面'])}</strong></td>
                    <td style="color: #666">{int(row['中性'])}</td>
                    <td><strong>{row['正面率']*100:.1f}%</strong></td>
                </tr>
        '''

    html += '''
            </tbody>
        </table>
    </div>
</div>

<script>
const chartL1Bar = echarts.init(document.getElementById('chart_l1_bar'));
chartL1Bar.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['正面', '负面', '中性'] },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: ['''

    l1_names = [f"'{row['一级类目']}'" for _, row in df_l1.head(15).iterrows()]
    html += ','.join(l1_names)

    html += '''] },
    series: [
        { name: '正面', type: 'bar', stack: 'total', data: ['''

    positive_data = [str(int(row['正面'])) for _, row in df_l1.head(15).iterrows()]
    html += ','.join(positive_data)

    html += '''], itemStyle: { color: '#22c55e' } },
        { name: '负面', type: 'bar', stack: 'total', data: ['''

    negative_data = [str(int(row['负面'])) for _, row in df_l1.head(15).iterrows()]
    html += ','.join(negative_data)

    html += '''], itemStyle: { color: '#ef4444' } },
        { name: '中性', type: 'bar', stack: 'total', data: ['''

    neutral_data = [str(int(row['中性'])) for _, row in df_l1.head(15).iterrows()]
    html += ','.join(neutral_data)

    html += '''], itemStyle: { color: '#94a3b8' } }
    ]
});

const chartL1Scatter = echarts.init(document.getElementById('chart_l1_scatter'));
chartL1Scatter.setOption({
    tooltip: { formatter: params => `<strong>${params.data[3]}</strong><br/>关注度: ${params.data[0]}<br/>满意度: ${params.data[1].toFixed(1)}%` },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '5%', containLabel: true },
    xAxis: { name: '关注度（提及次数）', nameLocation: 'middle', nameGap: 30 },
    yAxis: { name: '满意度（正面率%）', nameLocation: 'middle', nameGap: 50, min: 0, max: 100 },
    series: [{
        type: 'scatter',
        symbolSize: params => Math.sqrt(params[0]) * 3,
        data: ['''

    scatter_data = []
    for _, row in df_l1.iterrows():
        scatter_data.append(f"[{int(row['标签总数'])}, {row['正面率']*100:.1f}, 0, '{row['一级类目']}']")
    html += ',\n'.join(scatter_data)

    html += '''],
        itemStyle: {
            color: params => {
                const s = params.data[1];
                return s >= 75 ? '#22c55e' : (s >= 60 ? '#ffc107' : '#ef4444');
            },
            opacity: 0.7
        }
    }],
    markLine: {
        silent: true,
        lineStyle: { type: 'dashed', color: '#999' },
        data: [
            { yAxis: 50, label: { formatter: '50% 参考线' } },
            { yAxis: 75, label: { formatter: '75% 高满意度线' } }
        ]
    }
});

window.addEventListener('resize', () => {
    chartL1Bar.resize();
    chartL1Scatter.resize();
});
</script>
</body>
</html>
'''

    return html


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
        output_path = generate_voc_report(excel_path)
        print(f"报告已生成：{output_path}")
    else:
        print("用法: python report_generator.py <打标Excel路径>")
