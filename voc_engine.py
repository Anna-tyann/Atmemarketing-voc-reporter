#!/usr/bin/env python3
"""
VOC Engine — 核心打标与报告生成引擎
可参数化，支持不同产品品类
"""
import pandas as pd
import json
import re
from collections import defaultdict
from datetime import datetime
import os
import uuid

# ============================================================
# 0. 默认标签体系（品类通用框架）
# ============================================================
# 通用化的 DEFAULT_TAG_SYSTEM - 适配多品类
# 通用化标签体系 - 适配多品类（清洁、健康、美容、科技等）

DEFAULT_TAG_SYSTEM = {
    "核心功能与效果": {
        "color": "#2563eb",
        "l2": {
            "基础功能表现": {"match": ["clean", "cleaning", "cleaner", "works well", "does its job", "effective", "efficiently", "thorough", "deep", "powerful", "really works", "does a great job"]},
            "特定场景适配": {"match": ["specific", "special", "particular", "unique", "certain situation", "my case", "for my needs", "exactly what", "perfect for"]},
            "健康/舒适度改善": {"match": ["health", "healthy", "improve", "better", "feel better", "healthier", "comfortable", "relief", "soothe", "massage"]},
            "替代/升级其他产品": {"match": ["easier than", "instead of", "better than", "replaces", "upgrade from", "switched from", "not going back", "vs", "compared to"]},
            "深度清理能力": {"match": ["remove", "get rid of", "clear", "stuck", "debris", "leftover", "particle", "residue", "buildup", "get out"]},
        }
    },
    "性能表现": {
        "color": "#7c3aed",
        "l2": {
            "速度与效率": {"match": ["fast", "quick", "speed", "slow", "takes forever", "takes too long", "efficient", "time saving", "instant", "immediate"]},
            "动力/强度控制": {"match": ["power", "powerful", "strength", "strong", "weak", "gentle", "intensity", "force", "pressure", "mode", "setting", "level", "adjust"]},
            "运行噪音": {"match": ["noise", "noisy", "loud", "quiet", "silent", "sound", "whisper", "roar", "annoying sound"]},
            "容量与续航": {"match": ["capacity", "tank", "hold", "size", "enough", "not enough", "small", "large", "run out", "need more", "refill"]},
        }
    },
    "设计与做工": {
        "color": "#f59e0b",
        "l2": {
            "外观设计": {"match": ["look", "appearance", "aesthetic", "design", "stylish", "modern", "sleek", "pretty", "ugly", "cheap looking"]},
            "人机设计与握持感": {"match": ["ergonomic", "grip", "comfortable to hold", "easy to hold", "fits in hand", "handle", "lightweight", "light and easy", "balanced", "slim"]},
            "做工质量": {"match": ["build quality", "well made", "sturdy", "solid", "durable", "quality material", "premium feel", "good quality", "well built", "flimsy", "cheap plastic"]},
            "卫生与清洁维护": {"match": ["mold", "mildew", "bacteria", "sanitary", "hygiene", "clean the", "clean it", "maintain", "slime", "gunk", "dirty", "hard to clean"]},
            "密封与防漏": {"match": ["leak", "drip", "spill", "water everywhere", "mess", "seal", "tight", "secure", "waterproof", "wet"]},
        }
    },
    "便携性": {
        "color": "#10b981",
        "l2": {
            "体积大小": {"match": ["size", "compact", "small", "tiny", "bulky", "large", "huge", "space", "footprint", "takes up"]},
            "重量": {"match": ["weight", "heavy", "light", "lightweight", "portable", "carry", "lug around"]},
            "旅行与携带": {"match": ["travel", "trip", "vacation", "portable", "on the go", "bring with", "pack", "suitcase", "carry on"]},
        }
    },
    "电池与续航": {
        "color": "#ef4444",
        "l2": {
            "续航时长": {"match": ["battery life", "last", "run time", "charge", "hold charge", "battery drain", "die quickly", "long battery"]},
            "充电体验": {"match": ["charging", "charge time", "recharge", "USB", "wireless charge", "fast charge", "charger", "cable"]},
        }
    },
    "易用性": {
        "color": "#06b6d4",
        "l2": {
            "上手难度": {"match": ["easy to use", "simple", "straightforward", "intuitive", "complicated", "confusing", "hard to figure", "difficult", "learning curve"]},
            "操作便捷性": {"match": ["convenient", "hassle", "easy", "user friendly", "one button", "automatic", "effortless"]},
            "配件与存储": {"match": ["accessories", "tip", "attachment", "nozzle", "head", "storage", "case", "holder", "organize"]},
            "说明书清晰度": {"match": ["instruction", "manual", "guide", "directions", "clear", "confusing", "no manual", "hard to understand"]},
        }
    },
    "价格与价值": {
        "color": "#8b5cf6",
        "l2": {
            "价格评价": {"match": ["price", "cost", "expensive", "cheap", "affordable", "pricey", "overpriced", "reasonable"]},
            "性价比": {"match": ["value", "bang for buck", "worth it", "worth the money", "good deal", "bargain", "not worth", "great value"]},
        }
    },
    "可靠性与售后": {
        "color": "#ec4899",
        "l2": {
            "耐用性": {"match": ["durable", "durability", "last", "break", "broke", "stopped working", "longevity", "still going", "still works"]},
            "故障率": {"match": ["defect", "malfunction", "fail", "stopped", "died", "quit working", "broke down", "issue", "problem", "doesn't work"]},
            "售后服务": {"match": ["customer service", "support", "warranty", "replacement", "refund", "return", "contact", "response", "helped"]},
        }
    },
    "品牌与推荐度": {
        "color": "#f97316",
        "l2": {
            "品牌信任": {"match": ["brand", "trust", "reputation", "well known", "famous", "heard of", "reliable brand"]},
            "推荐意愿": {"match": ["recommend", "suggest", "tell friends", "worth buying", "must have", "don't buy", "stay away", "highly recommend"]},
        }
    },
    "整体评价": {
        "color": "#64748b",
        "l2": {
            "综合满意度": {"match": ["overall", "in general", "satisfied", "happy with", "pleased", "content", "disappointed", "unhappy"]},
            "超出/低于预期": {"match": ["expect", "expected", "surprise", "impressed", "amazing", "exceeded", "let down", "not as good", "better than expected"]},
            "极端好评": {"match": ["love", "best", "perfect", "amazing", "excellent", "fantastic", "wonderful", "favorite", "game changer", "life saver", "changed my life"]},
            "极端差评": {"match": ["worst", "terrible", "horrible", "awful", "disappointed", "waste", "useless", "junk", "garbage", "regret", "poor product", "not worth it", "don't bother", "stay away", "avoid", "hate it"]},
        }
    },
}

# 行为场景维度（12个）- 品类通用

BEHAVIORAL_DIMENSIONS = {
    "🎯 购买动因": {
        "color": "#f97316",
        "dim_type": "behavioral",
        "l2": {
            "专业人士推荐购买": {
                "match": ["professional recommend", "expert recommend", "specialist recommend", "doctor recommend",
                         "prescribed", "told me to get", "advised me", "specialist said", "recommended by"]
            },
            "社交媒体/短视频种草": {
                "match": ["saw on tiktok", "saw on youtube", "saw a video", "watched a review", "influencer",
                         "found on", "instagram ad", "facebook ad", "tiktok made me", "viral", "social media",
                         "online review", "amazon review", "saw this on", "video review"]
            },
            "朋友/家人推荐": {
                "match": ["friend recommend", "family recommend", "my mom", "my dad", "my sister", "my brother",
                         "my wife", "my husband", "coworker recommend", "neighbor", "someone told"]
            },
            "刚需驱动(特定问题)": {
                "match": ["need", "needed", "have to", "must", "necessary", "essential", "can't without",
                         "problem", "issue", "suffer", "struggle", "pain", "condition"]
            },
            "自用升级/替换旧产品": {
                "match": ["upgrade", "replace", "old one", "previous", "last one", "broke", "stopped working",
                         "better than", "improvement", "switched from"]
            },
            "礼物/送人购买": {
                "match": ["gift", "present", "for my", "bought for", "gave to", "as a gift", "christmas", "birthday"]
            },
        }
    },
    "📍 使用地点": {
        "color": "#3b82f6",
        "dim_type": "behavioral",
        "l2": {
            "家庭/室内": {
                "match": ["home", "house", "bathroom", "bedroom", "kitchen", "living room", "at home", "indoors"]
            },
            "户外/露营/房车": {
                "match": ["outdoor", "camping", "rv", "camper", "van", "travel", "on the road", "wilderness"]
            },
            "办公室/工作场所": {
                "match": ["office", "work", "workplace", "desk", "at work", "during work"]
            },
            "健身房/运动场": {
                "match": ["gym", "fitness", "workout", "locker room", "sports", "exercise"]
            },
        }
    },
    "⏰ 使用场景": {
        "color": "#8b5cf6",
        "dim_type": "behavioral",
        "l2": {
            "日常例行": {
                "match": ["daily", "every day", "morning", "evening", "routine", "regularly", "habit"]
            },
            "特定活动前后": {
                "match": ["before and after", "right before", "right after", "pre workout",
                         "post workout", "during my", "while i", "when i", "after using",
                         "before using", "before going", "after waking"]
            },
            "休闲时使用": {
                "match": ["watch tv", "relax", "leisure", "free time", "weekend", "downtime"]
            },
            "特殊场合/需求": {
                "match": ["special occasion", "event", "party", "date", "important", "when i need"]
            },
        }
    },
    "👤 用户画像": {
        "color": "#06b6d4",
        "dim_type": "behavioral",
        "l2": {
            "中老年用户(50+)": {
                "match": ["senior citizen", "senior cat", "senior dog", "elderly",
                         "retired", "at my age",
                         "in my 50s", "in my 60s", "in my 70s", "in my 80s",
                         "over 50", "over 60", "over 70",
                         "grandma", "grandpa", "grandparent", "great grandma",
                         "aging parent", "aging body", "aging joints",
                         "old age", "getting older", "older adult", "older people",
                         "older person", "older folks", "older couple",
                         "old man", "old lady", "old woman",
                         "i am 50", "i am 60", "i am 70", "i am 80",
                         "i'm 50", "i'm 60", "i'm 70", "i'm 80"]
            },
            "父母/家庭购买者": {
                "match": ["my kid", "my child", "my son", "my daughter", "my children", "my teenager",
                         "for the family", "whole family", "everyone in", "my toddler", "my little one"]
            },
            "商务/差旅人士": {
                "match": ["business travel", "work travel", "frequent traveler", "road warrior",
                         "business trip", "travel for work", "commuter", "on the go", "mobile professional"]
            },
            "新手/首次使用者": {
                "match": ["first time", "never used before", "new to this", "just started", "beginner",
                         "my first", "never tried", "new user", "just got my first", "first one"]
            },
            "重度/资深用户": {
                "match": ["i am obsessed", "addicted to", "can't live without", "my holy grail",
                         "swear by", "game changer", "best thing ever", "life changing", "changed my life"]
            },
        }
    },
    "💡 用户兴趣/生活方式": {
        "color": "#14b8a6",
        "dim_type": "behavioral",
        "l2": {
            "健康/养生关注": {
                "match": ["health", "healthy", "wellness", "preventive", "healthcare", "health conscious",
                         "take care of", "better health", "stay healthy", "health routine"]
            },
            "个人护理/美容达人": {
                "match": ["beauty routine", "self care", "personal care", "grooming", "skincare",
                         "beauty", "spa", "pampering", "treat yourself", "self love"]
            },
            "科技数码爱好者": {
                "match": ["gadget", "tech", "latest tech", "new technology", "smart device",
                         "tech savvy", "tech geek", "early adopter", "innovative", "high tech"]
            },
            "家庭/亲子导向": {
                "match": ["stay at home", "homemaker", "my family", "with kids", "full house",
                         "family of", "mom life", "dad life", "parenting", "household"]
            },
            "户外/运动爱好者": {
                "match": ["hiking", "camping", "outdoor", "fitness", "gym", "workout", "running",
                         "athletic", "sports", "active lifestyle", "on the trail", "backpacker"]
            },
            "性价比/精明消费者": {
                "match": ["best bang", "best value", "compare price", "did my research", "researched",
                         "shop around", "best deal", "budget", "save money", "cost effective"]
            },
        }
    },
    "🏷️ 品牌/竞品对比": {
        "color": "#f59e0b",
        "dim_type": "behavioral",
        "l2": {
            "竞品比较": {
                "match": ["better than", "compared to", "vs", "versus", "instead of", "switched from",
                         "tried other", "other brand", "comparison"]
            },
            "品牌忠诚": {
                "match": ["always buy", "only use", "stick with", "loyal", "trust this brand", "brand fan"]
            },
        }
    },
    "🔮 未满足需求/期望": {
        "color": "#ec4899",
        "dim_type": "behavioral",
        "l2": {
            "功能缺失": {
                "match": ["wish it had", "missing", "lacking", "doesn't have", "no", "would be better if",
                         "needs", "should have", "want"]
            },
            "性能不足": {
                "match": ["not strong enough", "not powerful", "weak", "could be better", "not as good",
                         "disappointing", "underwhelming"]
            },
            "体验优化建议": {
                "match": ["improve", "suggestion", "recommend adding", "hope they", "next version",
                         "future model", "upgrade"]
            },
        }
    },
    "🔄 复购/忠诚行为": {
        "color": "#10b981",
        "dim_type": "behavioral",
        "l2": {
            "复购/回购": {
                "match": ["bought again", "second one", "third one", "another one", "repurchase",
                         "buy more", "buying another", "ordered again"]
            },
            "推荐给他人": {
                "match": ["told my friend", "recommended to", "everyone should", "spread the word",
                         "bought one for", "got one for", "convinced"]
            },
            "品牌粉丝": {
                "match": ["fan", "love this brand", "always", "everything from", "loyal customer"]
            },
        }
    },
    "🛤️ 旅程阶段": {
        "color": "#64748b",
        "dim_type": "behavioral",
        "l2": {
            "研究对比阶段": {
                "match": ["researching", "looking into", "considering", "compare", "debating", "deciding"]
            },
            "首次使用体验": {
                "match": ["just got", "just received", "first time", "unboxing", "initial", "so far"]
            },
            "长期使用反馈": {
                "match": ["been using", "months", "years", "long term", "after", "still", "update"]
            },
        }
    },
    "📢 声音类型": {
        "color": "#f97316",
        "dim_type": "behavioral",
        "l2": {
            "推荐分享": {
                "match": ["recommend", "suggest", "must have", "best", "love", "highly", "everyone should"]
            },
            "竞品比较": {
                "match": ["compared to", "better than", "vs", "instead of", "switched from"]
            },
            "提问求助": {
                "match": ["how to", "how do", "question", "help", "anyone know", "does anyone", "is it"]
            },
            "感谢致意": {
                "match": ["thank you", "thanks", "grateful", "appreciate", "love it", "changed my life"]
            },
        }
    },
    "💥 实际后果/影响": {
        "color": "#ef4444",
        "dim_type": "behavioral",
        "l2": {
            "健康/舒适改善": {
                "match": ["feel better", "improvement", "relief", "no more pain", "stopped hurting",
                         "helped with", "comfortable", "healthier", "feeling better", "much better now",
                         "so much better", "feels so much", "no longer"]
            },
            "时间/效率提升": {
                "match": ["save time", "faster", "quick", "efficient", "convenient", "easy"]
            },
            "经济/成本影响": {
                "match": ["save money", "cheaper", "expensive", "worth it", "paid off", "investment"]
            },
        }
    },
    "🧠 心理/情感类型": {
        "color": "#a855f7",
        "dim_type": "behavioral",
        "l2": {
            "惊喜/超出预期": {
                "match": ["surprised", "wow", "amazed", "didn't expect", "better than expected",
                         "impressed", "blown away", "shocked"]
            },
            "安心/踏实": {
                "match": ["peace of mind", "feel safe", "reassuring", "confident", "trust", "reliable"]
            },
            "困惑/迷茫": {
                "match": ["confused", "don't understand", "not sure", "unclear", "complicated", "difficult"]
            },
            "失望/后悔": {
                "match": ["disappointed", "regret", "wish i hadn't", "let down", "not what i expected",
                         "waste", "returning"]
            },
        }
    },
}



# ============================================================
# 1. Excel 加载
# ============================================================
def load_excel(filepath):
    """加载Excel文件，返回DataFrame和元信息"""
    df = pd.read_excel(filepath)
    required = ['rid', 'title', 'content', 'rating']
    for col in required:
        if col not in df.columns:
            # Try case-insensitive match
            match = [c for c in df.columns if c.lower() == col.lower()]
            if match:
                df.rename(columns={match[0]: col}, inplace=True)
            else:
                raise ValueError(f"缺少必需列: {col}。请确保Excel包含 rid, title, content, rating 列。")

    df['title'] = df['title'].astype(str)
    df['content'] = df['content'].astype(str)
    if 'asin' not in df.columns:
        df['asin'] = 'N/A'
    else:
        df['asin'] = df['asin'].astype(str)
    if 'date' in df.columns:
        df['date'] = df['date'].astype(str)

    # 预览数据
    preview = {
        "total_rows": len(df),
        "columns": df.columns.tolist(),
        "rating_distribution": df['rating'].value_counts().sort_index().to_dict(),
        "avg_rating": round(df['rating'].mean(), 2),
        "sample_rows": df.head(5)[['rid', 'asin', 'title', 'rating']].to_dict(orient='records'),
        "asin_list": df['asin'].unique().tolist() if 'asin' in df.columns else [],
    }
    return df, preview


# ============================================================
# 2. 情感分析
# ============================================================
NEGATION_WORDS = ["not", "no", "never", "doesn't", "didn't", "won't", "can't",
                  "isn't", "aren't", "wasn't", "weren't", "hardly", "barely",
                  "struggle", "fail", "failed", "poor", "terrible", "horrible",
                  "useless", "worst", "waste", "junk", "garbage"]
STRONG_POSITIVE = ["love", "amazing", "fantastic", "excellent", "perfect",
                   "outstanding", "incredible", "wonderful", "best", "impressed",
                   "highly recommend", "game changer", "worth every penny"]
NEGATION_OF_NEGATIVE = {"leak", "leaking", "leakage", "hurt", "pain", "mess", "messy",
                        "problem", "issue", "damage", "defect", "noise", "complaint"}


def determine_tag_sentiment(text, rating, keywords_matched):
    """精准情感判断：评分主导 + 紧邻否定检测"""
    text_lower = text.lower()
    has_direct_negation = False
    has_direct_pos = False

    for kw in keywords_matched:
        idx = text_lower.find(kw)
        if idx < 0:
            continue
        words_before = text_lower[max(0, idx-30):idx].split()
        words_after = text_lower[idx+len(kw):idx+len(kw)+30].split()
        nearby = " ".join(words_before[-5:] + words_after[:5])

        for neg in NEGATION_WORDS:
            pat1 = rf'\b{re.escape(neg)}\b(?:\s+\w+){{0,3}}\s+{re.escape(kw)}'
            pat2 = rf'\b{re.escape(kw)}\b(?:\s+\w+){{0,3}}\s+{re.escape(neg)}'
            if re.search(pat1, text_lower) or re.search(pat2, text_lower):
                if kw in NEGATION_OF_NEGATIVE:
                    has_direct_pos = True
                else:
                    has_direct_negation = True
                break

        for pos in STRONG_POSITIVE:
            pat1 = rf'\b{re.escape(pos)}\b(?:\s+\w+){{0,4}}\s+{re.escape(kw)}'
            pat2 = rf'\b{re.escape(kw)}\b(?:\s+\w+){{0,4}}\s+{re.escape(pos)}'
            if re.search(pat1, text_lower) or re.search(pat2, text_lower):
                has_direct_pos = True
                break

    if rating >= 4:
        if has_direct_negation and not has_direct_pos:
            return "negative"
        return "positive"
    elif rating <= 2:
        if has_direct_pos and not has_direct_negation:
            return "positive"
        return "negative"
    else:
        if has_direct_pos and not has_direct_negation:
            return "positive"
        elif has_direct_negation and not has_direct_pos:
            return "negative"
        return "neutral"


def extract_quote(text, keywords_matched, max_len=120):
    """从评论中提取包含关键词的代表性原文片段"""
    text_clean = str(text).strip()
    if not text_clean:
        return ""
    sentences = re.split(r'(?<=[.!?])\s+', text_clean)
    best, best_score = None, 0
    for sent in sentences:
        score = sum(1 for kw in keywords_matched if kw in sent.lower())
        if score > best_score:
            best_score = score
            best = sent.strip()
    if not best:
        best = text_clean[:max_len] + ("..." if len(text_clean) > max_len else "")
    elif len(best) > max_len:
        best = best[:max_len] + "..."
    return best


# ============================================================
# 3. 辅助常量与工具函数
# ============================================================
DEFAULT_COLORS = [
    "#2563eb", "#7c3aed", "#f59e0b", "#10b981", "#ef4444",
    "#06b6d4", "#8b5cf6", "#ec4899", "#f97316", "#64748b",
    "#14b8a6", "#3b82f6", "#a855f7", "#6366f1", "#0ea5e9"
]

# ============================================================
# 3.5 关键词词边界匹配（避免子串误匹配，如 age->package, older->holder）
# ============================================================
_KW_PATTERN_CACHE = {}


def _kw_in_text(kw, text):
    """
    词边界匹配：关键词必须作为完整词/短语出现，而非任意子串。
    修复历史 bug：短词 'age' 命中 package/usage/damage，'older' 命中 holder，
    'aging' 命中 packaging，导致所有品类报告的用户画像都错误偏向"中老年用户"。

    - 首尾为字母/数字的关键词用 \\b 词边界包裹
    - 含空格的短语（如 'before and after'）同样按词边界匹配，内部空格允许任意空白
    """
    pat = _KW_PATTERN_CACHE.get(kw)
    if pat is None:
        # 关键词内部空白归一化为 \s+，允许 "over  50" / 换行等
        escaped = r"\s+".join(re.escape(part) for part in kw.split())
        left = r"\b" if kw[:1].isalnum() else ""
        right = r"\b" if kw[-1:].isalnum() else ""
        pat = re.compile(left + escaped + right)
        _KW_PATTERN_CACHE[kw] = pat
    return pat.search(text) is not None


# ============================================================
# 4. 标签提取主函数
# ============================================================
def extract_tags(df, tag_system, product_name="产品", progress_callback=None):
    """
    核心打标函数
    Args:
        df: pandas DataFrame with columns [rid, asin, title, content, rating]
        tag_system: dict of {l1_name: {color, l2: {l2_name: {match: [keywords]}}}}
        product_name: 产品名称
        progress_callback: optional callback(percent, message)
    Returns:
        dict with meta, tags, l1_stats, l2_data, pain_points, strengths, etc.
    """
    # 合并产品维度 + 行为场景维度（vocovoca 16维框架）
    full_tag_system = dict(tag_system)
    full_tag_system.update(BEHAVIORAL_DIMENSIONS)

    total_rows = len(df)
    tags = []

    for idx, row in df.iterrows():
        rid = str(row['rid'])
        asin = str(row.get('asin', 'N/A'))
        title = str(row['title'])
        content = str(row['content'])
        rating = int(row['rating'])
        full_text = (title + " " + content).lower()
        tagged_combos = set()

        for l1_name, l1_data in full_tag_system.items():
            for l2_name, l2_config in l1_data.get("l2", {}).items():
                combo_key = f"{l1_name}|{l2_name}"
                if combo_key in tagged_combos:
                    continue
                matched_kw = [kw for kw in l2_config.get("match", []) if _kw_in_text(kw, full_text)]
                if not matched_kw:
                    continue
                sentiment = determine_tag_sentiment(full_text, rating, matched_kw)
                quote = extract_quote(content if len(str(content)) > 20 else title, matched_kw)
                tags.append({
                    "rid": rid, "asin": asin, "l1": l1_name, "l2": l2_name,
                    "sentiment": sentiment, "rating": rating, "quote": quote,
                    "keywords": matched_kw[:5],
                })
                tagged_combos.add(combo_key)

        # 兜底标签
        if not tagged_combos:
            sentiment = "positive" if rating >= 4 else ("negative" if rating <= 2 else "neutral")
            l2_name = "整体满意度" if sentiment == "positive" else ("整体不满" if sentiment == "negative" else "整体满意度")
            tags.append({
                "rid": rid, "asin": asin, "l1": "整体评价", "l2": l2_name,
                "sentiment": sentiment, "rating": rating,
                "quote": str(content)[:120] if len(str(content)) > 20 else str(title)[:120],
                "keywords": [],
            })

        if progress_callback and total_rows > 0:
            progress_callback(int((idx + 1) / total_rows * 100), f"处理中 {idx+1}/{total_rows}")

    # --- 统计计算 ---
    l2_stats = defaultdict(lambda: {"l1": "", "l2": "", "total": 0, "positive": 0, "negative": 0, "neutral": 0, "quotes_pos": [], "quotes_neg": []})
    l1_stats = defaultdict(lambda: {"total": 0, "positive": 0, "negative": 0, "neutral": 0})

    for tag in tags:
        key = f"{tag['l1']}|{tag['l2']}"
        ls = l2_stats[key]
        ls["l1"] = tag["l1"]
        ls["l2"] = tag["l2"]
        ls["total"] += 1
        if tag["sentiment"] == "positive":
            ls["positive"] += 1
            if len(ls["quotes_pos"]) < 5:
                ls["quotes_pos"].append(tag["quote"])
        elif tag["sentiment"] == "negative":
            ls["negative"] += 1
            if len(ls["quotes_neg"]) < 5:
                ls["quotes_neg"].append(tag["quote"])
        else:
            ls["neutral"] += 1

        l1 = l1_stats[tag["l1"]]
        l1["total"] += 1
        if tag["sentiment"] == "positive":
            l1["positive"] += 1
        elif tag["sentiment"] == "negative":
            l1["negative"] += 1
        else:
            l1["neutral"] += 1

    total_tags = len(tags)
    total_pos = sum(1 for t in tags if t["sentiment"] == "positive")
    total_neg = sum(1 for t in tags if t["sentiment"] == "negative")
    total_neu = sum(1 for t in tags if t["sentiment"] == "neutral")

    # --- L2级数据 ---
    l1_sorted = sorted(l1_stats.items(), key=lambda x: -x[1]["total"])
    l1_order = {name: i for i, (name, _) in enumerate(l1_sorted)}

    l2_table = []
    scatter_l2 = []
    for key, stat in l2_stats.items():
        if stat["total"] >= 2:
            pos_rate = round(stat["positive"] / stat["total"] * 100, 1)
            l2_table.append({
                "l1": stat["l1"], "l2": stat["l2"], "mention": stat["total"],
                "positive": stat["positive"], "negative": stat["negative"],
                "positive_rate": pos_rate, "satisfaction_bar": pos_rate,
            })
            scatter_l2.append({
                "name": stat["l2"],
                "value": [stat["total"], pos_rate],
                "L1": stat["l1"],
                "positive": stat["positive"],
                "negative": stat["negative"],
            })
    l2_table.sort(key=lambda x: (l1_order.get(x["l1"], 99), -x["mention"]))

    # --- Pain Points & Strengths ---
    pain_points = []
    strengths_list = []
    for key, stat in l2_stats.items():
        if stat["total"] >= 2:
            pos_rate = stat["positive"] / stat["total"] * 100
            if pos_rate < 50 and stat["negative"] > 0:
                pain_points.append({
                    "l2_tag": stat["l2"], "l1_tag": stat["l1"],
                    "mention_count": stat["total"], "positive_rate": round(pos_rate, 1),
                    "positive": stat["positive"], "negative": stat["negative"],
                    "quotes": stat["quotes_neg"][:3],
                })
            if pos_rate >= 75 and stat["total"] >= 3 and stat["positive"] > 0:
                strengths_list.append({
                    "l2_tag": stat["l2"], "l1_tag": stat["l1"],
                    "mention_count": stat["total"], "positive_rate": round(pos_rate, 1),
                    "positive": stat["positive"], "negative": stat["negative"],
                    "quotes": stat["quotes_pos"][:3],
                })
    pain_points.sort(key=lambda x: (-x["mention_count"], x["positive_rate"]))
    strengths_list.sort(key=lambda x: (-x["mention_count"], -x["positive_rate"]))

    # --- Insights ---
    insights = auto_generate_insights(
        {"tags": tags, "l2_stats": l2_stats, "pain_points": pain_points, "strengths": strengths_list},
        product_name
    )

    # --- Cross Analysis Matrix ---
    cross_analysis = _generate_cross_analysis(tags, l1_stats)

    # --- Keyword WordCloud ---
    wordcloud_data = _generate_wordcloud_data(tags)

    # --- Chart Data ---
    l1_categories = [x[0] for x in l1_sorted if x[0] != "其他"]
    scatter_l1 = []
    for l1_name in l1_categories:
        s = l1_stats[l1_name]
        scatter_l1.append({
            "name": l1_name,
            "value": [s["total"], round(s["positive"] / s["total"] * 100, 1) if s["total"] > 0 else 0],
            "positive": s["positive"], "negative": s["negative"],
        })

    result = {
        "meta": {
            "product_name": product_name,
            "total_reviews": len(df),
            "total_tags": total_tags,
            "positive_rate": round(total_pos / total_tags * 100, 1) if total_tags > 0 else 0,
            "negative_rate": round(total_neg / total_tags * 100, 1) if total_tags > 0 else 0,
            "neutral_rate": round(total_neu / total_tags * 100, 1) if total_tags > 0 else 0,
            "avg_rating": round(df["rating"].mean(), 2),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "tags": tags,
        "l1_stats": {name: {
            "total": s["total"], "positive": s["positive"], "negative": s["negative"], "neutral": s["neutral"],
            "positive_rate": round(s["positive"] / s["total"] * 100, 1) if s["total"] > 0 else 0
        } for name, s in l1_stats.items()},
        "l2_table": l2_table,
        "scatter_l2": scatter_l2,
        "scatter_l1": scatter_l1,
        "bar_l1": {
            "categories": l1_categories,
            "positive": [l1_stats[c]["positive"] for c in l1_categories],
            "negative": [l1_stats[c]["negative"] for c in l1_categories],
            "neutral": [l1_stats[c]["neutral"] for c in l1_categories],
        },
        "pain_points": pain_points,
        "strengths": strengths_list,
        "personas": insights["personas"],
        "scenarios": insights["scenarios"],
        "recommendations": insights["recommendations"],
        "cross_analysis": cross_analysis,
        "wordcloud": wordcloud_data,
    }
    return result


# ============================================================
# 3.5. 交叉分析与词云数据生成
# ============================================================
def _generate_cross_analysis(tags, l1_stats):
    """
    生成维度交叉分析矩阵
    返回: {
        "matrices": [
            {"title": "用户画像 × 痛点维度", "rows": [...], "cols": [...], "data": [[count, ...], ...]},
            ...
        ]
    }
    """
    from collections import defaultdict

    # 定义交叉分析对
    cross_pairs = [
        ("👤 用户画像", ["核心功能与效果", "性能表现", "设计与做工", "易用性", "可靠性与售后"]),
        ("📍 使用地点", ["核心功能与效果", "便携性", "电池与续航", "易用性"]),
        ("⏰ 使用场景", ["核心功能与效果", "性能表现", "便携性", "电池与续航"]),
        ("📢 声音类型", ["整体评价", "品牌与推荐度", "价格与价值"]),
        ("🔮 未满足需求/期望", ["💥 实际后果/影响", "🧠 心理/情感类型"]),
    ]

    matrices = []

    for dim1_name, dim2_list in cross_pairs:
        # 统计共现
        co_occurrence = defaultdict(lambda: defaultdict(int))

        # 按 review 分组标签
        review_tags = defaultdict(list)
        for tag in tags:
            review_tags[tag['rid']].append(tag)

        # 计算共现次数
        for rid, tag_list in review_tags.items():
            l1_in_review = set(t['l1'] for t in tag_list)

            if dim1_name in l1_in_review:
                for dim2_name in dim2_list:
                    if dim2_name in l1_in_review:
                        # 获取具体的 L2 标签
                        dim1_l2s = [t['l2'] for t in tag_list if t['l1'] == dim1_name]
                        dim2_l2s = [t['l2'] for t in tag_list if t['l1'] == dim2_name]

                        for l2_1 in dim1_l2s:
                            for l2_2 in dim2_l2s:
                                co_occurrence[l2_1][l2_2] += 1

        # 如果有数据，构建矩阵
        if co_occurrence:
            rows = sorted(co_occurrence.keys(), key=lambda x: sum(co_occurrence[x].values()), reverse=True)[:8]
            all_cols = set()
            for r in rows:
                all_cols.update(co_occurrence[r].keys())
            cols = sorted(all_cols, key=lambda x: sum(co_occurrence[r].get(x, 0) for r in rows), reverse=True)[:8]

            data = []
            for row in rows:
                data.append([co_occurrence[row].get(col, 0) for col in cols])

            matrices.append({
                "title": f"{dim1_name} × {', '.join(dim2_list[:2])}{'等' if len(dim2_list) > 2 else ''}",
                "rows": rows,
                "cols": cols,
                "data": data
            })

    return {"matrices": matrices}


def _generate_wordcloud_data(tags):
    """
    从标签的 keywords 中提取高频词，生成词云数据
    返回: [{"name": "word", "value": count}, ...]
    """
    from collections import Counter
    import re

    # 停用词
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does',
        'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
        'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its',
        'our', 'their', 'me', 'him', 'us', 'them', 'what', 'which', 'who', 'when', 'where', 'why',
        'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
        'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just',
        've', 'll', 'm', 're', 'd'
    }

    # 收集所有 keywords
    word_counter = Counter()
    for tag in tags:
        keywords = tag.get('keywords', [])
        for kw in keywords:
            # 分词并清理
            words = re.findall(r'\b[a-zA-Z]{3,}\b', kw.lower())
            for word in words:
                if word not in stopwords and len(word) > 2:
                    word_counter[word] += 1

    # 取 Top 80
    top_words = word_counter.most_common(80)

    return [{"name": word, "value": count} for word, count in top_words]


# ============================================================
# 4. 自动洞察生成
# ============================================================
def auto_generate_insights(tags_data, product_name):
    """基于标签数据自动生成用户画像、使用场景和改进建议"""
    l2_stats = tags_data.get("l2_stats", {})
    pain_points = tags_data.get("pain_points", [])
    strengths_list = tags_data.get("strengths", [])

    # 自动推断画像
    personas = _generate_personas(tags_data, product_name)
    scenarios = _generate_scenarios(tags_data, product_name)
    recommendations = _generate_recommendations(pain_points, strengths_list, product_name)

    return {
        "personas": personas,
        "scenarios": scenarios,
        "recommendations": recommendations,
    }


def _generate_personas(tags_data, product_name):
    """
    完全数据驱动：从实际打标的 '👤 用户画像' 维度提取真实画像。
    不再使用硬编码模板，避免出现不适配品类的画像（如猫抓板的"便携/移动需求用户"）。
    """
    from collections import defaultdict
    tags = tags_data.get("tags", [])

    # 各 L2 用户画像标签的 icon 映射（品类通用）
    persona_icons = {
        "中老年用户(50+)": "👴", "父母/家庭购买者": "👨‍👩‍👧", "商务/差旅人士": "💼",
        "新手/首次使用者": "🌱", "重度/资深用户": "⭐", "科技数码爱好者": "🔧",
        "性价比/精明消费者": "💰", "礼物购买者": "🎁", "专业需求用户": "🧑‍⚕️",
    }

    # 聚合 👤 用户画像 维度下的 L2 标签
    persona_stats = defaultdict(lambda: {"total": 0, "positive": 0, "quotes": []})
    for t in tags:
        if "用户画像" in t.get("l1", ""):
            l2 = t.get("l2", "")
            persona_stats[l2]["total"] += 1
            if t.get("sentiment") == "positive":
                persona_stats[l2]["positive"] += 1
            q = t.get("quote", "").strip()
            if q and len(q) > 15 and len(persona_stats[l2]["quotes"]) < 2:
                persona_stats[l2]["quotes"].append(q)

    # 按提及次数排序，取真实存在的画像
    sorted_personas = sorted(persona_stats.items(), key=lambda x: -x[1]["total"])

    personas = []
    for l2_name, stat in sorted_personas[:6]:
        if stat["total"] < 1:
            continue
        pos_rate = round(stat["positive"] / stat["total"] * 100) if stat["total"] > 0 else 0
        personas.append({
            "name": l2_name,
            "icon": persona_icons.get(l2_name, "👤"),
            "desc": f"该群体在评论中被提及 {stat['total']} 次，正面率 {pos_rate}%。"
                    f"是{product_name}的重要目标用户之一，值得针对性运营。",
            "quotes": stat["quotes"],
        })

    # 数据不足时的兜底（仍基于真实数据，仅提示）
    if not personas:
        personas.append({
            "name": "核心用户群", "icon": "👤",
            "desc": f"当前评论中用户画像维度标签较少，建议补充更多评论数据以获得精准画像。",
            "quotes": [],
        })

    return personas


def _generate_scenarios(tags_data, product_name):
    """
    完全数据驱动：从实际打标的 '📍 使用地点' + '⏰ 使用场景' 维度提取真实场景。
    不再使用硬编码模板（如冲牙器的"旅行/出差场景"）。
    """
    from collections import defaultdict
    tags = tags_data.get("tags", [])

    # 场景 L2 标签的 icon 映射（品类通用）
    scenario_icons = {
        "家庭/室内": "🏠", "户外/露营/房车": "🏕️", "办公室/工作场所": "🏢",
        "健身房/运动场": "💪", "日常例行": "📅", "特定活动前后": "⏰",
        "休闲时使用": "🛋️", "特殊场合/需求": "🎯",
    }

    # 聚合 使用地点 + 使用场景 维度下的 L2 标签
    scenario_stats = defaultdict(lambda: {"total": 0, "positive": 0, "l1": ""})
    for t in tags:
        l1 = t.get("l1", "")
        if "使用地点" in l1 or "使用场景" in l1:
            l2 = t.get("l2", "")
            scenario_stats[l2]["total"] += 1
            scenario_stats[l2]["l1"] = l1
            if t.get("sentiment") == "positive":
                scenario_stats[l2]["positive"] += 1

    sorted_scenarios = sorted(scenario_stats.items(), key=lambda x: -x[1]["total"])

    scenarios = []
    for l2_name, stat in sorted_scenarios[:4]:
        if stat["total"] < 1:
            continue
        pos_rate = round(stat["positive"] / stat["total"] * 100) if stat["total"] > 0 else 0
        dim_type = "使用地点" if "使用地点" in stat["l1"] else "使用时机"
        scenarios.append({
            "name": l2_name,
            "icon": scenario_icons.get(l2_name, "📍"),
            "desc": f"【{dim_type}】评论中被提及 {stat['total']} 次，正面率 {pos_rate}%。"
                    f"是{product_name}的核心使用场景，可用于场景化营销和网站视觉设计。",
        })

    if not scenarios:
        scenarios.append({
            "name": "日常使用场景", "icon": "🏠",
            "desc": f"当前评论中使用场景维度标签较少，建议补充更多评论数据。",
        })

    return scenarios


def _generate_recommendations(pain_points, strengths_list, product_name):
    """基于痛点自动生成改进建议"""
    recs = []

    # P0: 从痛点中生成
    for pp in pain_points[:4]:
        recs.append({
            "title": f"改进{pp['l2_tag']}",
            "priority": "高",
            "desc": f"当前{pp['l2_tag']}正面率仅{pp['positive_rate']}%，{pp['mention_count']}次提及中{pp['negative']}条为负面。"
                    f"这是用户集中反映的痛点，建议作为产品迭代的高优先级事项。"
        })

    # P1: 从低提及但高关注的标签
    for s in strengths_list[:4]:
        recs.append({
            "title": f"强化{s['l2_tag']}优势",
            "priority": "中",
            "desc": f"{s['l2_tag']}正面率{s['positive_rate']}%，是产品核心优势。"
                    f"建议在营销中重点突出，并持续保持这一优势。"
        })

    # 补充通用建议
    if len(recs) < 6:
        recs.append({
            "title": f"提升整体品控与可靠性",
            "priority": "高",
            "desc": f"加强出厂质检流程，减少DOA（到手即坏）和早期故障问题，提供更完善的质保服务。"
        })
        recs.append({
            "title": f"优化{product_name}用户体验细节",
            "priority": "中",
            "desc": f"基于用户反馈持续优化产品的人机交互、操作便利性和使用舒适度，打造卓越的用户体验。"
        })

    return recs[:8]


def _find_relevant_quotes(tags, triggers, count=2):
    """从标签中找与trigger相关的quote"""
    quotes = []
    for tag in tags:
        q = tag.get("quote", "").lower()
        if any(t in q for t in triggers):
            quotes.append(tag["quote"])
            if len(quotes) >= count:
                break
    if not quotes:
        quotes = [t.get("quote", "") for t in tags[:count]]
    return quotes


# ============================================================
# 5. HTML 报告生成
# ============================================================
def build_report_html(tags_data, product_config=None):
    """
    生成完整的独立HTML报告
    Args:
        tags_data: extract_tags() 返回的完整字典
        product_config: {product_name, category, tag_system} 或 None
    Returns:
        str: 完整的HTML报告
    """
    if product_config is None:
        product_config = {}

    product_name = product_config.get("product_name", tags_data["meta"].get("product_name", "产品"))
    tag_system = product_config.get("tag_system", {})

    # Merge behavioral dimension colors
    full_colors = {}
    for i, (l1_name, l1_data) in enumerate(tag_system.items()):
        full_colors[l1_name] = l1_data.get("color", DEFAULT_COLORS[i % len(DEFAULT_COLORS)])
    for l1_name, l1_data in BEHAVIORAL_DIMENSIONS.items():
        full_colors[l1_name] = l1_data.get("color", "#6b7280")

    colors = full_colors if full_colors else {
        name: DEFAULT_COLORS[i % len(DEFAULT_COLORS)]
        for i, name in enumerate(tags_data.get("l1_stats", {}).keys())
    }
    # 确保整体评价有颜色
    if "整体评价" not in colors:
        colors["整体评价"] = "#0d9488"

    meta = tags_data["meta"]
    scatter_l2 = tags_data["scatter_l2"]
    scatter_l1 = tags_data["scatter_l1"]
    bar_l1 = tags_data["bar_l1"]
    l2_table = tags_data["l2_table"]
    pain_points = tags_data["pain_points"]
    strengths_list = tags_data["strengths"]
    personas = tags_data["personas"]
    scenarios = tags_data["scenarios"]
    recommendations = tags_data["recommendations"]

    # Extract behavioral dimension insights for marketing conclusion
    l1_stats = tags_data.get("l1_stats", {})
    purchase_motivations = [k.replace("🎯 购买动因>","") for k in l1_stats if "购买动因" in k]
    user_persona_dim = [k.replace("👤 用户画像>","") for k in l1_stats if "用户画像" in k]
    usage_locations = [k.replace("📍 使用地点>","") for k in l1_stats if "使用地点" in k]
    user_interests = [k.replace("💡 用户兴趣/生活方式>","") for k in l1_stats if "用户兴趣/生活方式" in k]
    brand_comparisons = [k.replace("🏷️ 品牌/竞品对比>","") for k in l1_stats if "品牌/竞品对比" in k]
    loyalty_behaviors = [k.replace("🔄 复购/忠诚行为>","") for k in l1_stats if "复购/忠诚行为" in k]
    unmet_needs = [k.replace("🔮 未满足需求/期望>","") for k in l1_stats if "未满足需求/期望" in k]

    # Get behavior count summaries
    behavior_l1 = {k: v for k, v in l1_stats.items() if any(d in k for d in ["购买动因","使用地点","用户画像","用户兴趣","品牌/竞品","复购/忠诚","使用场景","未满足需求"])}
    has_behavioral = len(behavior_l1) > 0

    def _esc(s):
        return str(s).replace('"', '\\"').replace('\n', ' ')

    # Build HTML sections
    def build_exec_summary():
        top_pain = pain_points[:3]
        top_str = strengths_list[:3]
        pain_text = "、".join([f"{p['l2_tag']}（正面率仅{p['positive_rate']}%）" for p in top_pain]) if top_pain else "部分维度"
        str_text = "、".join([f"{s['l2_tag']}（正面率{s['positive_rate']}%）" for s in top_str]) if top_str else "多个维度"

        # Behavioral insight teaser
        behavior_lines = []
        if has_behavioral:
            mot_l1 = [k for k in behavior_l1 if "购买动因" in k]
            loc_l1 = [k for k in behavior_l1 if "使用地点" in k]
            per_l1 = [k for k in behavior_l1 if "用户画像" in k]
            if mot_l1:
                behavior_lines.append(f"提取<span class=\"highlight\">购买动因</span>{behavior_l1[mot_l1[0]]['total']}条")
            if loc_l1:
                behavior_lines.append(f"<span class=\"highlight\">使用地点</span>{behavior_l1[loc_l1[0]]['total']}条")
            if per_l1:
                behavior_lines.append(f"<span class=\"highlight\">用户画像</span>{behavior_l1[per_l1[0]]['total']}条")
        behavior_teaser = "、".join(behavior_lines) if behavior_lines else ""

        return f"""<p class="summary-text">
      本次分析覆盖 <span class="highlight">{meta['total_reviews']} 条用户评论</span>，共提取 {meta['total_tags']} 条标签标注，涵盖 {len(tags_data.get('l1_stats',{}))} 个分析维度（含产品功能+行为场景+用户画像），涉及 {len(scatter_l2)} 个细分标签。
      总体来看，用户对{product_name}产品的正面评价占比 {meta['positive_rate']}%，表明大部分用户对产品核心功能持肯定态度。
      但也有 <span class="highlight-red">{meta['negative_rate']}% 的负面评价</span>集中暴露在{pain_text}等关键维度。
      {f"此外，" + behavior_teaser + "，为社媒内容策略、网红合作和精准投放提供了数据支撑。" if behavior_teaser else ""}
    </p>"""

    def build_scatter_l2_js():
        lines = ["var scatterData = ["]
        for d in scatter_l2:
            lines.append(f'  {{"name": "{_esc(d["name"])}", "value": [{d["value"][0]}, {d["value"][1]}], "L1": "{_esc(d["L1"])}", "positive": {d["positive"]}, "negative": {d["negative"]}}},')
        lines.append("];")
        return "\n".join(lines)

    def build_bar_l1_js():
        return f"var barData = {json.dumps(bar_l1, ensure_ascii=False)};"

    def build_scatter_l1_js():
        lines = ["var l1Data = ["]
        for d in scatter_l1:
            lines.append(f'  {{"name": "{_esc(d["name"])}", "value": [{d["value"][0]}, {d["value"][1]}], "positive": {d["positive"]}, "negative": {d["negative"]}}},')
        lines.append("];")
        return "\n".join(lines)

    def build_tag_table():
        rows = []
        for d in l2_table:
            bar_w = max(3, int(float(d["satisfaction_bar"]) * 1.5))
            bar_color = "#22c55e" if d["positive_rate"] >= 75 else ("#f59e0b" if d["positive_rate"] >= 50 else "#ef4444")
            rows.append(f'<tr><td>{d["l1"]}</td><td>{d["l2"]}</td><td>{d["mention"]}</td><td>{d["positive"]}</td><td>{d["negative"]}</td><td>{d["positive_rate"]}%</td><td><span class="bar-inline" style="width:{bar_w}px; background:{bar_color}"></span> </td></tr>')
        return "\n".join(rows)

    def build_pain_points():
        cards = []
        for p in pain_points[:8]:
            quotes_html = "\n".join([f'<div class="quote">{_esc(q)}</div>' for q in p.get("quotes", [])[:3]])
            cards.append(f"""<div class="insight-card pain">
      <h4>{p['l2_tag']}（提及{p['mention_count']}次 · 正面率仅{p['positive_rate']}%）</h4>
      <p>正面率低于50%，共{p.get('negative', 0)}条负面提及。</p>
      {quotes_html}
    </div>""")
        return "\n".join(cards) if cards else "<p>暂无显著痛点数据</p>"

    def build_strengths():
        cards = []
        for s in strengths_list[:6]:
            quotes_html = "\n".join([f'<div class="quote">{_esc(q)}</div>' for q in s.get("quotes", [])[:3]])
            cards.append(f"""<div class="insight-card strength">
      <h4>{s['l2_tag']}（提及{s['mention_count']}次 · 正面率{s['positive_rate']}%）</h4>
      <p>用户高度认可，共{s.get('positive', 0)}条正面提及。</p>
      {quotes_html}
    </div>""")
        return "\n".join(cards) if cards else "<p>暂无显著优势数据</p>"

    def build_personas():
        cards = []
        for p in personas:
            cards.append(f"""<div class="persona-card">
      <div class="persona-icon">{p.get('icon', '👤')}</div>
      <h4>{p['name']}</h4>
      <p>{p['desc']}</p>
    </div>""")
        return "\n".join(cards)

    def build_scenarios():
        cards = []
        for s in scenarios:
            cards.append(f"""<div class="scenario-card">
      <h4>{s.get('icon', '📍')} {s['name']}</h4>
      <p>{s['desc']}</p>
    </div>""")
        return "\n".join(cards)

    def build_recommendations():
        cards = []
        for r in recommendations:
            cls = "priority-high" if r["priority"] == "高" else "priority-mid"
            cards.append(f"""<div class="rec-card">
      <span class="priority {cls}">优先级：{r['priority']}</span>
      <h4>{r['title']}</h4>
      <p>{r['desc']}</p>
    </div>""")
        return "\n".join(cards)

    def build_cross_analysis():
        """构建交叉分析矩阵的 HTML + 热力图"""
        cross_data = tags_data.get('cross_analysis', {})
        matrices = cross_data.get('matrices', [])

        if not matrices:
            return '<p style="color:#94a3b8;">暂无交叉分析数据</p>'

        html_parts = []
        for idx, matrix in enumerate(matrices):
            title = matrix['title']
            rows = matrix['rows']
            cols = matrix['cols']
            data = matrix['data']

            # 表格
            table_html = f'<h4 style="margin:24px 0 12px;color:#334155;">{title}</h4>'
            table_html += '<div style="overflow-x:auto;"><table class="data-table" style="font-size:0.88em;"><thead><tr><th style="min-width:120px;">维度</th>'
            for col in cols:
                table_html += f'<th style="min-width:100px;">{col}</th>'
            table_html += '</tr></thead><tbody>'

            for i, row in enumerate(rows):
                table_html += f'<tr><td><b>{row}</b></td>'
                for val in data[i]:
                    color = '#f1f5f9' if val == 0 else f'rgba(37, 99, 235, {min(val/20, 0.8)})'
                    table_html += f'<td style="background:{color};text-align:center;">{val if val > 0 else "-"}</td>'
                table_html += '</tr>'
            table_html += '</tbody></table></div>'

            # 热力图
            heatmap_id = f'heatmap-{idx}'
            table_html += f'<div id="{heatmap_id}" class="chart-container" style="height:400px;margin-top:16px;"></div>'

            html_parts.append(table_html)

        return "\n".join(html_parts)

    def build_wordcloud_js():
        """生成词云的 JS 数据"""
        wordcloud_data = tags_data.get('wordcloud', [])
        return json.dumps(wordcloud_data, ensure_ascii=False)


    def build_marketing_strategy():
        """基于实际标签数据动态生成营销战略方向"""
        def _top_l2(l1_prefix, n=3, min_mention=1):
            items = [d for d in l2_table if l1_prefix in d['l1']]
            items.sort(key=lambda x: -x['mention'])
            return [d for d in items[:n] if d['mention'] >= min_mention]

        def _find_quotes(l1_prefix, l2_name=None, sentiment=None, n=2):
            result = []
            for t in tags_data.get('tags', []):
                if l1_prefix not in t['l1']:
                    continue
                if l2_name and t['l2'] != l2_name:
                    continue
                if sentiment and t['sentiment'] != sentiment:
                    continue
                q = t.get('quote', '').strip()
                if q and len(q) > 15:
                    result.append(q)
                    if len(result) >= n:
                        break
            return result

        def _extract_competitor_names():
            """从评论中提取竞品名称（通用方法：大写开头的连续词 + 常见品牌模式）"""
            names = set()
            # 通用竞品识别：从 "竞品对比" 标签的 quote/keywords 中提取品牌名
            for t in tags_data.get('tags', []):
                if '品牌/竞品对比' in t['l1'] or '竞品对比' in t['l2']:
                    text = t.get('quote', '') + ' ' + ' '.join(t.get('keywords', []))
                    # 提取大写开头的单词（可能是品牌名）
                    import re
                    brands = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', text)
                    # 过滤掉常见非品牌词
                    stop_words = {'This', 'That', 'Which', 'When', 'Where', 'What', 'Why', 'How',
                                 'The', 'My', 'Your', 'Their', 'Better', 'Good', 'Bad', 'Great',
                                 'Love', 'Hate', 'Much', 'Very', 'Really', 'Just', 'More', 'Less'}
                    for b in brands:
                        if b not in stop_words and len(b) > 2:
                            names.add(b)
            return sorted(names)[:5]

        # Extract real data
        top_motivations = _top_l2('购买动因', n=4)
        top_locations = _top_l2('使用地点', n=3)
        top_scenarios = _top_l2('使用场景', n=3)
        top_personas = _top_l2('用户画像', n=3)
        top_interests = _top_l2('用户兴趣/生活方式', n=4)
        top_unmet = _top_l2('未满足需求', n=3)
        top_loyalty = _top_l2('复购/忠诚行为', n=2)
        competitor_names = _extract_competitor_names()
        recommend_quotes = _find_quotes('声音类型', '推荐分享', 'positive', n=3)
        if not recommend_quotes:
            recommend_quotes = _find_quotes('声音类型', None, 'positive', n=3)
        compare_quotes = _find_quotes('声音类型', '竞品比较', None, n=2)

        # ── Card 1: Social Media Content Strategy ──
        content_lines = []
        if top_motivations:
            m = top_motivations[:3]
            mot_text = '、'.join([f"「{d['l2']}」({d['mention']}次)" for d in m])
            content_lines.append(f'<b>① 购买动因驱动</b>：用户Top购买动因为 {mot_text}，据此规划口碑推荐、自用升级、送礼场景等内容线')
        if pain_points:
            p = pain_points[0]
            content_lines.append(f'<b>② 痛点共鸣型</b>：抓住最大痛点「{p["l2_tag"]}」（正面率仅{p["positive_rate"]}%），制作「从痛点到解决方案」的转变故事')
        if recommend_quotes:
            q = recommend_quotes[0][:100]
            content_lines.append(f'<b>③ 真实UGC素材</b>：利用高赞评论如「{q}...」制作口碑短视频，保留用户真实语言风格')

        persona_desc = '、'.join([d['l2'] for d in top_personas]) if top_personas else '核心用户群'
        content_html = f'''<div class="insight-card strength">
          <h4>🎬 社媒内容策略</h4>
          <p>基于{len(top_motivations)}个购买动因和{len(top_personas)}类用户画像，{product_name}的核心用户群体为<b>{persona_desc}</b>，内容应聚焦以下角度：</p>
          <p style="margin-top:6px;">{"<br>".join(content_lines) if content_lines else '<p>数据量不足以生成精确内容策略。</p>'}</p>
          <p style="margin-top:8px;font-size:0.88em;color:#64748b;">💡 <b>执行建议</b>：每篇内容对应一个具体购买动因，使用真实quote中的语言风格。情感hook优先使用评论中出现的真实用户故事。</p>
        </div>'''

        # ── Card 2: Influencer Strategy ──
        inf_lines = []
        if top_locations:
            loc_text = '、'.join([f'「{d["l2"]}」' for d in top_locations[:2]])
            inf_lines.append(f'① <b>场景类达人</b>：覆盖{loc_text}等使用场景的垂类红人（基于📍使用地点Top{len(top_locations)}标签）')
        if top_interests:
            int_text = '、'.join([f'「{d["l2"]}」' for d in top_interests[:3]])
            inf_lines.append(f'② <b>兴趣圈层KOL</b>：匹配{int_text}等兴趣领域创作者（基于💡用户兴趣/生活方式Top{len(top_interests)}标签）')
        if top_personas:
            per_text = '、'.join([f'「{d["l2"]}」' for d in top_personas[:2]])
            inf_lines.append(f'③ <b>人群定向达人</b>：受众与{per_text}重合度高的红人（基于👤用户画像维度）')
        if competitor_names:
            inf_lines.append(f'④ <b>对比测评博主</b>：可合作{", ".join(competitor_names[:3])}等竞品的对比评测（基于真实竞品提及数据）')
        brf = recommend_quotes[0][:100] if recommend_quotes else ''
        inf_html = f'''<div class="insight-card strength">
          <h4>🤝 海外网红合作方向</h4>
          <p>基于实际用户数据和标签分析，<b>网红筛选策略</b>如下：</p>
          <p style="margin-top:6px;">{"<br>".join(inf_lines) if inf_lines else '<p>数据量不足以生成精确网红筛选建议。</p>'}</p>
          <p style="margin-top:8px;font-size:0.88em;color:#64748b;">💡 <b>Brief素材</b>：将真实用户quote提供给网红作为脚本参考。''' + (f'例如「{brf}...」让网红围绕真实用户痛点进行创作，增强真实感和转化率。' if brf else '') + f'''</p>
        </div>'''

        # ── Card 3: Website & Landing Page ──
        web_lines = []
        if top_locations:
            web_lines.append(f'① <b>Hero区视觉</b>：以「{top_locations[0]["l2"]}」为核心场景主视觉（{top_locations[0]["mention"]}次提及）')
        if recommend_quotes:
            web_lines.append(f'② <b>用户证言轮播</b>：首页植入真实评价如「{recommend_quotes[0][:80]}...」')
        if pain_points:
            pain_web = '、'.join([p['l2_tag'] for p in pain_points[:3]])
            web_lines.append(f'③ <b>痛点解决方案专区</b>：针对「{pain_web}」分别设置解决模块')
        if competitor_names:
            web_lines.append(f'④ <b>竞品对比页</b>：基于用户真实提及的{", ".join(competitor_names[:2])}创建对比模块')
        if top_loyalty:
            loy_web = '、'.join([d['l2'] for d in top_loyalty])
            web_lines.append(f'⑤ <b>社交证明</b>：展示「{loy_web}」相关数据（基于🔄复购/忠诚行为维度）')
        web_html = f'''<div class="insight-card strength">
          <h4>🌐 网站与落地页优化</h4>
          <p>基于真实用户行为数据，<b>转化优化策略</b>：</p>
          <p style="margin-top:6px;">{"<br>".join(web_lines) if web_lines else '<p>数据量不足以生成精确网站优化建议。</p>'}</p>
          <p style="margin-top:8px;font-size:0.88em;color:#64748b;">💡 <b>FAQ板块</b>：优先回答用户评论中高频出现的实际问题，这些数据直接来自用户真实困惑而非品牌主观猜测。</p>
        </div>'''

        # ── Card 4: Ad Targeting ──
        ad_lines = []
        if pain_points and top_personas:
            ad_lines.append(f'① <b>痛点人群包</b>：定向关注「{pain_points[0]["l2_tag"]}」问题的用户（{pain_points[0]["mention_count"]}次提及，正面率仅{pain_points[0]["positive_rate"]}%），以解决方案为hook')
        elif pain_points:
            ad_lines.append(f'① <b>痛点人群包</b>：定向关注「{pain_points[0]["l2_tag"]}」问题的用户，以「解决{pain_points[0]["l2_tag"]}」为hook')
        if top_locations and pain_points:
            ad_lines.append(f'② <b>场景定向人群</b>：对「{top_locations[0]["l2"]}」场景用户投放痛点解决方案素材（该场景{top_locations[0]["mention"]}次提及）')
        if competitor_names:
            ad_lines.append(f'③ <b>竞品截流人群</b>：定向搜索「{competitor_names[0]}」等竞品的用户，投放真实用户对比证言素材')
        if top_interests:
            int_ad = '、'.join([d['l2'] for d in top_interests[:2]])
            ad_lines.append(f'④ <b>兴趣扩量人群</b>：基于「{int_ad}」等兴趣标签做Lookalike相似人群扩展')
        ad_html = f'''<div class="insight-card strength">
          <h4>🎯 精准投放人群包</h4>
          <p>基于用户画像 × 购买动因 × 兴趣三维交叉分析，<b>核心投放人群</b>：</p>
          <p style="margin-top:6px;">{"<br>".join(ad_lines) if ad_lines else '<p>数据量不足以生成精确投放人群建议。</p>'}</p>
          <p style="margin-top:8px;font-size:0.88em;color:#64748b;">💡 <b>素材差异化策略</b>：每组人群使用不同hook — 痛点人群用「终于解决了[具体痛点]」，场景人群用「在[使用场景]中发现」，竞品人群用「为什么我从[竞品]换成{product_name}」，兴趣人群用「让[兴趣标签]更轻松的秘诀」。</p>
        </div>'''

        # ── Summary section ──
        product_dims = sum(1 for k in l1_stats if not any(k.startswith(e) for e in ['🎯','📍','⏰','👤','💡','🏷️','🔮','🔄']))
        behavioral_dims = len(l1_stats) - product_dims
        tps = f'「{pain_points[0]["l2_tag"]}」' if pain_points else ''
        tss = f'「{strengths_list[0]["l2_tag"]}」' if strengths_list else ''
        comp_summary = '本次分析识别出竞品提及：' + '、'.join(competitor_names) + '，可作为竞争对标和截流营销的数据基础。' if competitor_names else ''

        return f'''<div class="section">
      <div class="section-title">📌 总结与营销战略方向</div>
      <p class="summary-text">
        基于{meta['total_reviews']}条用户评论的{meta['total_tags']}个标签深度分析，覆盖<b>{product_dims}个产品功能维度</b>和<b>{behavioral_dims}个行为场景维度</b>，
        {product_name}的核心用户洞察可转化为以下<b>数据驱动的营销战略方向</b>：
      </p>
      <div class="insight-grid">
        {content_html}
        {inf_html}
        {web_html}
        {ad_html}
      </div>
      <p class="summary-text" style="margin-top:16px;">
        <b>数据驱动总结</b>：从{meta['total_reviews']}条评论中提取的核心发现 —
        最大痛点是{tps or '可靠性相关维度'}，最大优势是{tss or '产品核心功能'}。
        建议每季度更新VOC分析，持续追踪用户关注点变化，及时调整策略。
        {comp_summary}
      </p>
    </div>'''
    # Assemble full HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{product_name}用户评论深度分析报告</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/echarts-wordcloud@2.1.0/dist/echarts-wordcloud.min.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif; background: #f0f4f8; color: #1e293b; line-height: 1.8; }}
  .header {{ background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 50%, #7c3aed 100%); color: white; padding: 60px 40px 50px; text-align: center; position: relative; overflow: hidden; }}
  .header::before {{ content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%); animation: pulse 8s infinite; }}
  @keyframes pulse {{ 0%,100% {{ transform: scale(1); }} 50% {{ transform: scale(1.1); }} }}
  .header h1 {{ font-size: 2.4em; font-weight: 700; margin-bottom: 12px; position: relative; letter-spacing: 2px; }}
  .header .subtitle {{ font-size: 1.1em; opacity: 0.9; position: relative; }}
  .container {{ max-width: 1280px; margin: 0 auto; padding: 0 24px; }}
  .kpi-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: -35px auto 30px; position: relative; z-index: 10; }}
  .kpi-card {{ background: white; border-radius: 16px; padding: 28px 24px; text-align: center; box-shadow: 0 4px 24px rgba(0,0,0,0.08); transition: transform 0.2s; }}
  .kpi-card:hover {{ transform: translateY(-4px); }}
  .kpi-number {{ font-size: 2.6em; font-weight: 700; background: linear-gradient(135deg, #2563eb, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
  .kpi-label {{ font-size: 0.95em; color: #64748b; margin-top: 4px; }}
  .section {{ background: white; border-radius: 16px; padding: 36px 40px; margin-bottom: 28px; box-shadow: 0 2px 16px rgba(0,0,0,0.05); }}
  .section-title {{ font-size: 1.5em; font-weight: 700; color: #1e293b; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 3px solid #2563eb; display: inline-block; }}
  .chart-container {{ width: 100%; margin: 20px 0; }}
  .insight-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 20px; }}
  .insight-card {{ border-radius: 12px; padding: 24px; border-left: 4px solid; }}
  .insight-card.pain {{ background: #fef2f2; border-color: #ef4444; }}
  .insight-card.strength {{ background: #f0fdf4; border-color: #22c55e; }}
  .insight-card h4 {{ font-size: 1.1em; margin-bottom: 8px; }}
  .insight-card.pain h4 {{ color: #dc2626; }}
  .insight-card.strength h4 {{ color: #16a34a; }}
  .quote {{ background: rgba(0,0,0,0.04); border-radius: 8px; padding: 10px 16px; margin: 8px 0; font-style: italic; color: #475569; font-size: 0.92em; border-left: 3px solid #94a3b8; }}
  .quote::before {{ content: '\\201C'; font-size: 1.4em; color: #94a3b8; margin-right: 4px; }}
  .persona-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-top: 20px; }}
  .persona-card {{ border-radius: 16px; padding: 28px; text-align: center; border: 2px solid #e2e8f0; transition: all 0.3s; }}
  .persona-card:hover {{ border-color: #2563eb; box-shadow: 0 8px 30px rgba(37,99,235,0.15); }}
  .persona-icon {{ font-size: 3em; margin-bottom: 12px; }}
  .persona-card h4 {{ font-size: 1.15em; color: #1e293b; margin-bottom: 8px; }}
  .persona-card p {{ font-size: 0.9em; color: #64748b; }}
  .rec-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 20px; }}
  .rec-card {{ border-radius: 14px; padding: 28px; background: linear-gradient(135deg, #eff6ff, #f5f3ff); border: 1px solid #ddd6fe; }}
  .rec-card h4 {{ color: #4338ca; font-size: 1.1em; margin-bottom: 10px; }}
  .rec-card .priority {{ display: inline-block; padding: 2px 10px; border-radius: 10px; font-size: 0.78em; font-weight: 600; margin-bottom: 10px; }}
  .priority-high {{ background: #fee2e2; color: #dc2626; }}
  .priority-mid {{ background: #fef3c7; color: #d97706; }}
  .data-table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 0.9em; }}
  .data-table th {{ background: #f1f5f9; padding: 12px 16px; text-align: left; font-weight: 600; color: #475569; border-bottom: 2px solid #e2e8f0; }}
  .data-table td {{ padding: 10px 16px; border-bottom: 1px solid #f1f5f9; }}
  .data-table tr:hover {{ background: #f8fafc; }}
  .bar-inline {{ height: 8px; border-radius: 4px; display: inline-block; vertical-align: middle; }}
  .footer {{ text-align: center; padding: 40px; color: #94a3b8; font-size: 0.88em; }}
  .scenario-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 20px; }}
  .scenario-card {{ border-radius: 12px; padding: 24px; background: #f8fafc; border: 1px solid #e2e8f0; }}
  .scenario-card h4 {{ color: #2563eb; margin-bottom: 8px; }}
  .l1-tag-legend {{ display: flex; flex-wrap: wrap; gap: 12px; margin: 16px 0; justify-content: center; }}
  .legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 0.85em; color: #475569; }}
  .legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
  .summary-text {{ font-size: 1.02em; color: #334155; line-height: 2; }}
  .highlight {{ background: linear-gradient(transparent 60%, #bfdbfe 60%); padding: 0 2px; font-weight: 500; }}
  .highlight-red {{ background: linear-gradient(transparent 60%, #fecaca 60%); padding: 0 2px; font-weight: 500; }}
  @media (max-width: 768px) {{
    .kpi-row {{ grid-template-columns: repeat(2, 1fr); }}
    .insight-grid, .rec-grid, .persona-grid, .scenario-grid {{ grid-template-columns: 1fr; }}
    .section {{ padding: 24px 20px; }}
  }}
</style>
</head>
<body>

<div class="header">
  <h1>{product_name} · 用户评论深度分析报告</h1>
  <div class="subtitle">基于 {meta['total_reviews']} 条真实用户评论 · {meta['total_tags']} 个标签打标结果 · 数据驱动的产品洞察</div>
</div>

<div class="container">

<div class="kpi-row">
  <div class="kpi-card"><div class="kpi-number">{meta['total_reviews']}</div><div class="kpi-label">评论总数</div></div>
  <div class="kpi-card"><div class="kpi-number">{meta['total_tags']}</div><div class="kpi-label">标签标注数</div></div>
  <div class="kpi-card"><div class="kpi-number">{meta['positive_rate']}%</div><div class="kpi-label">整体正面率</div></div>
  <div class="kpi-card"><div class="kpi-number" style="-webkit-text-fill-color:#dc2626">{meta['negative_rate']}%</div><div class="kpi-label">整体负面率</div></div>
</div>

<div class="section"><div class="section-title">📋 核心发现摘要</div>{build_exec_summary()}</div>

<div class="section">
  <div class="section-title">📊 标签全景散点图：提及次数 vs 正面率</div>
  <p style="color:#64748b; margin-bottom:8px; font-size:0.92em;">横轴为提及次数（关注度），纵轴为正面率（满意度）。气泡大小代表提及次数。</p>
  <div class="l1-tag-legend" id="legend-container"></div>
  <div id="scatter-l2" class="chart-container" style="height:560px;"></div>
</div>

<div class="section">
  <div class="section-title">📈 一级标签维度：情感分布概览</div>
  <div id="bar-l1" class="chart-container" style="height:420px;"></div>
</div>

<div class="section">
  <div class="section-title">🔍 一级标签散点图：关注度 vs 满意度</div>
  <div id="scatter-l1" class="chart-container" style="height:420px;"></div>
</div>

<div class="section">
  <div class="section-title">🚨 核心用户痛点深度解读</div>
  <div class="insight-grid">{build_pain_points()}</div>
</div>

<div class="section">
  <div class="section-title">✅ 产品核心优势与用户认可点</div>
  <div class="insight-grid">{build_strengths()}</div>
</div>

<div class="section">
  <div class="section-title">👥 目标用户画像</div>
  <div class="persona-grid">{build_personas()}</div>
</div>

<div class="section">
  <div class="section-title">🎯 核心使用场景</div>
  <div class="scenario-grid">{build_scenarios()}</div>
</div>

<div class="section">
  <div class="section-title">💡 产品开发与优化建议</div>
  <div class="rec-grid">{build_recommendations()}</div>
</div>

<div class="section">
  <div class="section-title">🔗 维度交叉分析矩阵</div>
  <p style="color:#64748b; margin-bottom:16px; font-size:0.92em;">不同行为维度之间的共现关系，帮助发现用户群体的深层需求模式和痛点来源。</p>
  {build_cross_analysis()}
</div>

<div class="section">
  <div class="section-title">☁️ 用户高频关键词词云</div>
  <p style="color:#64748b; margin-bottom:16px; font-size:0.92em;">从 {meta['total_tags']} 条标签中提取的高频关键词，字体越大表示出现频率越高。</p>
  <div id="wordcloud" class="chart-container" style="height:500px;"></div>
</div>


<div class="section">
  <div class="section-title">📑 附录：标签体系明细表（一级 → 二级）</div>
  <p style="color:#64748b; margin-bottom:8px; font-size:0.92em;">完整标签数据，按一级类目分组，展示所有二级标签的提及次数、正负面分布和正面率。</p>
  <table class="data-table">
    <thead><tr><th>一级类目</th><th>二级标签</th><th>提及</th><th>正面</th><th>负面</th><th>正面率</th><th>满意度条</th></tr></thead>
    <tbody>{build_tag_table()}</tbody>
  </table>
</div>

{build_marketing_strategy()}
</div>
<div class="footer">
  {product_name}用户评论分析报告 · 基于 {meta['total_reviews']} 条评论 · {meta['total_tags']} 条标签 · 生成于 {meta['generated_at']}
</div>

<script>
var colorMap = {json.dumps(colors, ensure_ascii=False)};

// Legend
var legendContainer = document.getElementById('legend-container');
Object.keys(colorMap).forEach(function(name) {{
  if (name === '其他') return;
  var item = document.createElement('div');
  item.className = 'legend-item';
  item.innerHTML = '<span class="legend-dot" style="background:' + colorMap[name] + '"></span>' + name;
  legendContainer.appendChild(item);
}});

// Scatter L2
{build_scatter_l2_js()}
// 自适应气泡大小：根据最大提及次数动态调整缩放比例
var maxMentionL2 = Math.max.apply(null, scatterData.map(function(d) {{ return d.value[0]; }}));
var bubbleScaleL2 = maxMentionL2 > 200 ? 0.25 : (maxMentionL2 > 100 ? 0.4 : (maxMentionL2 > 50 ? 0.8 : 1.5));
var maxBubbleSizeL2 = 60;  // L2标签气泡最大直径
var seriesMap = {{}};
scatterData.forEach(function(d) {{
  if (!seriesMap[d.L1]) seriesMap[d.L1] = [];
  seriesMap[d.L1].push(d);
}});
var scatterSeries = [];
Object.keys(seriesMap).forEach(function(l1) {{
  scatterSeries.push({{
    name: l1, type: 'scatter',
    data: seriesMap[l1].map(function(d) {{
      var size = Math.min(Math.max(d.value[0] * bubbleScaleL2, 12), maxBubbleSizeL2);
      return {{
        name: d.name, value: d.value,
        symbolSize: size,
        itemStyle: {{ color: colorMap[l1] || '#6b7280' }},
        label: {{ show: d.value[0] >= 8, formatter: d.name, position: 'right', fontSize: 11, color: '#475569' }}
      }};
    }}),
    emphasis: {{ label: {{ show: true, formatter: function(p) {{ return p.name; }}, fontSize: 13, fontWeight: 'bold' }} }}
  }});
}});
var chart1 = echarts.init(document.getElementById('scatter-l2'));
chart1.setOption({{
  tooltip: {{ trigger: 'item', formatter: function(p) {{ return '<b>' + p.name + '</b><br/>提及次数: ' + p.value[0] + '<br/>正面率: ' + p.value[1] + '%'; }} }},
  grid: {{ left: '8%', right: '5%', top: '8%', bottom: '12%' }},
  xAxis: {{ name: '提及次数', nameLocation: 'center', nameGap: 30, nameTextStyle: {{ fontSize: 14, color: '#475569' }}, splitLine: {{ lineStyle: {{ type: 'dashed', color: '#e2e8f0' }} }} }},
  yAxis: {{ name: '正面率 (%)', nameLocation: 'center', nameGap: 40, nameTextStyle: {{ fontSize: 14, color: '#475569' }}, min: 0, max: 105, splitLine: {{ lineStyle: {{ type: 'dashed', color: '#e2e8f0' }} }}, axisLabel: {{ formatter: '{{value}}%' }} }},
  series: scatterSeries
}});
chart1.setOption({{ series: scatterSeries.map(function(s, i) {{
  if (i === 0) {{
    s.markLine = {{ silent: true, symbol: 'none', label: {{ show: true, position: 'insideEndTop', color: '#ef4444', fontSize: 11 }}, data: [{{ yAxis: 50, lineStyle: {{ color: '#ef4444', type: 'dashed', width: 1 }}, label: {{ formatter: '50% 满意度分界线' }} }}] }};
  }}
  return s;
}}) }});

// Bar L1
{build_bar_l1_js()}
var chart2 = echarts.init(document.getElementById('bar-l1'));
chart2.setOption({{
  tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }} }},
  legend: {{ data: ['正面', '负面', '中性'], top: 0 }},
  grid: {{ left: '14%', right: '5%', top: '12%', bottom: '5%' }},
  yAxis: {{ type: 'category', data: barData.categories.slice().reverse(), axisLabel: {{ fontSize: 12 }} }},
  xAxis: {{ type: 'value', name: '标注数量' }},
  series: [
    {{ name: '正面', type: 'bar', stack: 'total', data: barData.positive.slice().reverse(), itemStyle: {{ color: '#22c55e' }}, barWidth: '55%' }},
    {{ name: '负面', type: 'bar', stack: 'total', data: barData.negative.slice().reverse(), itemStyle: {{ color: '#ef4444' }} }},
    {{ name: '中性', type: 'bar', stack: 'total', data: barData.neutral.slice().reverse(), itemStyle: {{ color: '#f59e0b' }} }}
  ]
}});

// Scatter L1
{build_scatter_l1_js()}
var chart3 = echarts.init(document.getElementById('scatter-l1'));
// 自适应气泡大小：根据最大提及次数动态调整缩放比例
var maxMention = Math.max.apply(null, l1Data.map(function(d) {{ return d.value[0]; }}));
var bubbleScale = maxMention > 200 ? 0.3 : (maxMention > 100 ? 0.5 : 0.8);
var maxBubbleSize = 80;  // 最大气泡直径限制
chart3.setOption({{
  tooltip: {{ trigger: 'item', formatter: function(p) {{ return '<b>' + p.name + '</b><br/>提及次数: ' + p.value[0] + '<br/>正面率: ' + p.value[1] + '%<br/>正面: ' + p.data.positive + ' / 负面: ' + p.data.negative; }} }},
  grid: {{ left: '8%', right: '5%', top: '8%', bottom: '12%' }},
  xAxis: {{ name: '提及次数', nameLocation: 'center', nameGap: 30, nameTextStyle: {{ fontSize: 14, color: '#475569' }}, splitLine: {{ lineStyle: {{ type: 'dashed', color: '#e2e8f0' }} }} }},
  yAxis: {{ name: '正面率 (%)', nameLocation: 'center', nameGap: 40, nameTextStyle: {{ fontSize: 14, color: '#475569' }}, min: 0, max: 105, splitLine: {{ lineStyle: {{ type: 'dashed', color: '#e2e8f0' }} }}, axisLabel: {{ formatter: '{{value}}%' }} }},
  series: [{{
    type: 'scatter',
    data: l1Data.map(function(d) {{
      var size = Math.min(Math.max(d.value[0] * bubbleScale, 20), maxBubbleSize);
      return {{ name: d.name, value: d.value, positive: d.positive, negative: d.negative, symbolSize: size, itemStyle: {{ color: colorMap[d.name] || '#6b7280' }}, label: {{ show: true, formatter: d.name, position: 'right', fontSize: 12, color: '#334155', fontWeight: 500 }} }};
    }})
  }}, {{
    type: 'scatter', data: [],
    markLine: {{ silent: true, symbol: 'none', data: [
      {{ yAxis: 50, lineStyle: {{ color: '#ef4444', type: 'dashed', width: 1 }}, label: {{ formatter: '50% 分界线', position: 'insideEndTop', color: '#ef4444' }} }},
      {{ xAxis: 40, lineStyle: {{ color: '#3b82f6', type: 'dashed', width: 1 }}, label: {{ formatter: '高关注度', position: 'insideEndTop', color: '#3b82f6' }} }}
    ] }}
  }}]
}});

// Cross Analysis Heatmaps
var crossData = {json.dumps(tags_data.get('cross_analysis', {}).get('matrices', []), ensure_ascii=False)};
crossData.forEach(function(matrix, idx) {{
  var heatmapId = 'heatmap-' + idx;
  var heatmapEl = document.getElementById(heatmapId);
  if (!heatmapEl) return;

  var chartHeat = echarts.init(heatmapEl);
  var heatData = [];
  matrix.data.forEach(function(row, i) {{
    row.forEach(function(val, j) {{
      heatData.push([j, i, val]);
    }});
  }});

  chartHeat.setOption({{
    tooltip: {{ position: 'top', formatter: function(p) {{ return matrix.rows[p.value[1]] + ' × ' + matrix.cols[p.value[0]] + ': ' + p.value[2] + ' 次'; }} }},
    grid: {{ left: '18%', right: '5%', top: '5%', bottom: '18%' }},
    xAxis: {{ type: 'category', data: matrix.cols, splitArea: {{ show: true }}, axisLabel: {{ rotate: 45, fontSize: 11 }} }},
    yAxis: {{ type: 'category', data: matrix.rows, splitArea: {{ show: true }}, axisLabel: {{ fontSize: 11 }} }},
    visualMap: {{ min: 0, max: Math.max.apply(null, heatData.map(function(d) {{ return d[2]; }})), calculable: true, orient: 'horizontal', left: 'center', bottom: '0%', inRange: {{ color: ['#f0f9ff', '#bfdbfe', '#60a5fa', '#2563eb', '#1e40af'] }} }},
    series: [{{ name: '共现次数', type: 'heatmap', data: heatData, label: {{ show: true, fontSize: 10 }}, emphasis: {{ itemStyle: {{ shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' }} }} }}]
  }});
}});

// WordCloud
var wordcloudData = {build_wordcloud_js()};
if (wordcloudData.length > 0) {{
  var chartCloud = echarts.init(document.getElementById('wordcloud'));
  chartCloud.setOption({{
    tooltip: {{ show: true, formatter: function(p) {{ return p.name + ': ' + p.value + ' 次'; }} }},
    series: [{{
      type: 'wordCloud',
      shape: 'circle',
      left: 'center',
      top: 'center',
      width: '90%',
      height: '90%',
      sizeRange: [14, 52],
      rotationRange: [-30, 30],
      rotationStep: 15,
      gridSize: 8,
      drawOutOfBound: false,
      textStyle: {{
        fontFamily: 'Noto Sans SC, sans-serif',
        fontWeight: 'bold',
        color: function() {{
          var colors = ['#2563eb', '#7c3aed', '#db2777', '#ea580c', '#059669', '#0891b2'];
          return colors[Math.floor(Math.random() * colors.length)];
        }}
      }},
      emphasis: {{ focus: 'self', textStyle: {{ shadowBlur: 10, shadowColor: '#333' }} }},
      data: wordcloudData
    }}]
  }});
}}

window.addEventListener('resize', function() {{ chart1.resize(); chart2.resize(); chart3.resize(); }});
</script>
</body>
</html>"""

    return html


# ============================================================
# 6. 标签体系管理
# ============================================================
def save_tag_system(tag_system, filepath):
    """保存标签体系到JSON文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(tag_system, f, ensure_ascii=False, indent=2)

def load_tag_system(filepath):
    """从JSON文件加载标签体系"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def get_default_tag_system():
    """返回默认的标签体系框架"""
    import copy
    return copy.deepcopy(DEFAULT_TAG_SYSTEM)

def create_empty_tag_system():
    """创建空的标签体系模板"""
    return {
        "整体评价": {
            "color": "#0d9488",
            "l2": {
                "整体满意度": {"match": ["great", "excellent", "amazing", "love", "good", "happy", "satisfied"]},
                "整体不满": {"match": ["terrible", "bad", "worst", "disappointed", "waste", "regret"]},
            }
        }
    }


# ============================================================
# 7. 便捷函数：一键运行全流程
# ============================================================
def run_full_pipeline(excel_path, tag_system=None, product_name="产品", product_config=None):
    """
    一键运行：Excel → 打标 → 报告HTML
    Returns: (tags_data_dict, report_html_string)
    """
    if tag_system is None:
        tag_system = get_default_tag_system()

    df, preview = load_excel(excel_path)
    tags_data = extract_tags(df, tag_system, product_name)

    if product_config is None:
        product_config = {}
    product_config.setdefault("product_name", product_name)
    product_config.setdefault("tag_system", tag_system)

    report_html = build_report_html(tags_data, product_config)
    return tags_data, report_html, preview


# ============================================================
# 8. 打标结果导出到 Excel（打标完成版）
# ============================================================
def export_tagged_excel(df, tags_data, output_path, original_excel_path=None):
    """
    将打标结果回写到 Excel，生成「打标完成版」
    新增列：
    - 标签数量: 该评论匹配到的标签总数
    - 正面标签: 正面标签的 L1>L2 列表
    - 负面标签: 负面标签的 L1>L2 列表
    - 标签明细: 完整标签 JSON 字符串

    Args:
        df: 原始 DataFrame
        tags_data: extract_tags() 返回的字典
        output_path: 输出 Excel 路径（如 '打标完成版.xlsx'）
        original_excel_path: 如果提供，保留原始 Excel 的所有 sheet 和格式
    Returns:
        output_path
    """
    from collections import defaultdict

    # 按 rid 聚合标签
    rid_tags = defaultdict(list)
    for t in tags_data["tags"]:
        rid_tags[str(t["rid"])].append(t)

    # 新增列
    df_out = df.copy()
    df_out["标签数量"] = 0
    df_out["正面标签"] = ""
    df_out["负面标签"] = ""
    df_out["中性标签"] = ""
    df_out["标签明细"] = ""

    for idx, row in df_out.iterrows():
        rid = str(row["rid"])
        review_tags = rid_tags.get(rid, [])

        pos_tags = []
        neg_tags = []
        neu_tags = []
        detail_parts = []

        for t in review_tags:
            sentiment_emoji = {"positive": "✅", "negative": "❌", "neutral": "➖"}
            emoji = sentiment_emoji.get(t["sentiment"], "")
            detail_parts.append(f'{emoji} {t["l1"]} > {t["l2"]}')

            if t["sentiment"] == "positive":
                pos_tags.append(f'{t["l1"]}>{t["l2"]}')
            elif t["sentiment"] == "negative":
                neg_tags.append(f'{t["l1"]}>{t["l2"]}')
            else:
                neu_tags.append(f'{t["l1"]}>{t["l2"]}')

        df_out.at[idx, "标签数量"] = len(review_tags)
        df_out.at[idx, "正面标签"] = " | ".join(pos_tags)
        df_out.at[idx, "负面标签"] = " | ".join(neg_tags)
        df_out.at[idx, "中性标签"] = " | ".join(neu_tags)
        df_out.at[idx, "标签明细"] = "；".join(detail_parts)

    # 写入 Excel
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # Sheet 1: 打标数据（原始列 + 标签列）
        sheet_name = f'{tags_data["meta"].get("product_name", "产品")}_打标数据'
        if len(sheet_name) > 31:
            sheet_name = "打标数据"  # Excel sheet name max 31 chars
        df_out.to_excel(writer, sheet_name=sheet_name, index=False)

        # Sheet 2: L1 统计
        l1_rows = []
        for name, stat in tags_data.get("l1_stats", {}).items():
            l1_rows.append({
                "一级类目": name,
                "标签总数": stat["total"],
                "正面": stat["positive"],
                "负面": stat["negative"],
                "中性": stat["neutral"],
                "正面率": f'{stat["positive_rate"]}%',
            })
        pd.DataFrame(l1_rows).to_excel(writer, sheet_name="L1统计", index=False)

        # Sheet 3: L2 详情
        l2_rows = []
        for d in tags_data.get("l2_table", []):
            l2_rows.append({
                "一级类目": d["l1"],
                "二级标签": d["l2"],
                "提及次数": d["mention"],
                "正面": d["positive"],
                "负面": d["negative"],
                "正面率": f'{d["positive_rate"]}%',
            })
        pd.DataFrame(l2_rows).to_excel(writer, sheet_name="L2详情", index=False)

        # Sheet 4: 痛点+优势
        insights_rows = []
        for p in tags_data.get("pain_points", []):
            insights_rows.append({
                "类型": "痛点",
                "标签": f'{p["l1_tag"]}>{p["l2_tag"]}',
                "提及次数": p["mention_count"],
                "正面率": f'{p["positive_rate"]}%',
                "原文引用": " | ".join(p.get("quotes", [])[:2]),
            })
        for s in tags_data.get("strengths", []):
            insights_rows.append({
                "类型": "优势",
                "标签": f'{s["l1_tag"]}>{s["l2_tag"]}',
                "提及次数": s["mention_count"],
                "正面率": f'{s["positive_rate"]}%',
                "原文引用": " | ".join(s.get("quotes", [])[:2]),
            })
        pd.DataFrame(insights_rows).to_excel(writer, sheet_name="洞察汇总", index=False)

    print(f"✅ 打标完成版已保存: {output_path}")
    print(f"   Sheet 1: 打标数据 ({len(df_out)}行, 含{len(df.columns)}原始列+5标签列)")
    print(f"   Sheet 2: L1统计 ({len(l1_rows)}个类目)")
    print(f"   Sheet 3: L2详情 ({len(l2_rows)}个标签)")
    print(f"   Sheet 4: 洞察汇总 ({len(insights_rows)}条)")
    return output_path


def tag_and_export(excel_path, tag_system=None, product_name="产品", output_path=None):
    """
    一步完成：读取 Excel → 打标 → 导出打标完成版 Excel
    这是最常用的入口函数

    Args:
        excel_path: 原始 Excel 路径
        tag_system: 标签体系（None=使用默认）
        product_name: 产品名称
        output_path: 输出路径（None=自动生成「产品名_打标完成版.xlsx」）
    Returns:
        (tags_data, output_path)
    """
    import os

    if tag_system is None:
        tag_system = get_default_tag_system()

    df, preview = load_excel(excel_path)
    tags_data = extract_tags(df, tag_system, product_name)

    if output_path is None:
        base_dir = os.path.dirname(excel_path) or "."
        safe_name = product_name.replace(" ", "_").replace("/", "_")
        output_path = os.path.join(base_dir, f"{safe_name}_打标完成版.xlsx")

    export_tagged_excel(df, tags_data, output_path)

    # 同时保存 JSON
    json_path = output_path.replace(".xlsx", ".json")
    import json
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(tags_data, f, ensure_ascii=False, indent=2)
    print(f"💾 JSON 数据已同步保存: {json_path}")

    return tags_data, output_path


print("✅ voc_engine.py 已就绪")
print("  核心函数: load_excel, extract_tags, build_report_html, run_full_pipeline, tag_and_export")
print("  辅助函数: auto_generate_insights, save_tag_system, load_tag_system, export_tagged_excel")
