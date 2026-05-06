"""推荐验证页面 - 课堂验证算法命中率"""
import streamlit as st
import csv
import os
from collections import Counter
from datetime import datetime
from db_utils import get_connection

st.set_page_config(page_title="出游推荐验证", page_icon="🎯")
st.title("🎯 今天去哪儿玩？")
st.caption("回答两个问题，系统为你推荐最合适的出游目的地")
st.divider()

PATH_MAPPING = {
    "A-A-A-A-A": [3], "A-A-A-A-B": [2, 10],
    "A-A-A-B-A": [14], "A-A-A-B-B": [1, 4],
    "A-B-A-A-A": [14], "A-B-A-A-B": [1],
    "B-A-A-A-A": [20], "B-A-A-A-B": [19],
    "B-A-A-B-A": [28], "B-A-A-B-B": [30],
    "B-A-B-A-A": [17], "B-A-B-A-B": [29],
    "B-A-B-B-A": [22], "B-A-B-B-B": [21],
    "A-A-B-A-A": [9], "A-A-B-A-B": [7],
    "A-A-B-B-A": [8], "A-A-B-B-B": [6],
    "A-B-A-B-A": [4, 13], "A-B-A-B-B": [13, 4],
    "A-B-B-A-A": [12, 11], "A-B-B-A-B": [11, 12],
    "A-B-B-B-A": [5, 6, 15], "A-B-B-B-B": [15, 6, 5],
    "B-B-A-A-A": [18, 24], "B-B-A-A-B": [24, 18],
    "B-B-A-B-A": [23], "B-B-A-B-B": [26],
    "B-B-B-A-A": [25, 23], "B-B-B-A-B": [23, 25],
    "B-B-B-B-A": [16], "B-B-B-B-B": [27],
}

ITEM_NAMES = {
    1: "东湖绿道（磨山段）骑行", 2: "东湖落雁景区散步",
    3: "华科校内喻家湖环湖", 4: "华科森林公园徒步",
    5: "光谷步行街逛街", 6: "光谷天地探店",
    7: "K11购物艺术中心", 8: "关山大道咖啡馆",
    9: "光谷书房/独立书店", 10: "藏龙岛湿地公园",
    11: "光谷周边密室逃脱", 12: "光谷周边剧本杀",
    13: "光谷国际网球中心", 14: "花山生态城绿道骑行",
    15: "鲁巷广场/光谷广场聚餐", 16: "黄鹤楼",
    17: "昙华林文艺街区", 18: "粮道街美食探店",
    19: "汉口江滩散步", 20: "武昌江滩/长江大桥",
    21: "湖北省博物馆", 22: "武汉美术馆",
    23: "楚河汉街", 24: "万松园美食街",
    25: "江汉路步行街", 26: "武汉天地",
    27: "武汉欢乐谷", 28: "东湖樱花园",
    29: "武汉大学（建筑/樱花）", 30: "龟山公园/汉阳江滩",
}

ITEM_TAGS = {
    1: "🚴 骑行 · 户外 · 免费", 2: "🌿 散步 · 安静 · 免费",
    3: "🌊 环湖 · 安静 · 免费", 4: "🌲 徒步 · 运动 · 免费",
    5: "🛍️ 逛街 · 社交 · 中消费", 6: "☕ 探店 · 文艺 · 中消费",
    7: "🎨 看展 · 购物 · 中消费", 8: "☕ 咖啡 · 安静 · 低消费",
    9: "📖 书店 · 文艺 · 免费", 10: "🦆 湿地 · 安静 · 免费",
    11: "🔐 密室 · 刺激 · 中消费", 12: "🎭 剧本杀 · 社交 · 中消费",
    13: "🎾 网球 · 运动 · 低消费", 14: "🚴 骑行 · 户外 · 免费",
    15: "🍜 聚餐 · 社交 · 中消费", 16: "🏯 历史 · 风景 · 中消费",
    17: "🎨 文艺 · 拍照 · 免费", 18: "🍜 美食 · 小吃 · 低消费",
    19: "🌊 江景 · 散步 · 免费", 20: "🌉 江景 · 散步 · 免费",
    21: "🏛️ 文化 · 看展 · 免费", 22: "🖼️ 艺术 · 安静 · 免费",
    23: "🛍️ 购物 · 美食 · 中消费", 24: "🍜 美食 · 小吃 · 低消费",
    25: "🛍️ 逛街 · 购物 · 中消费", 26: "✨ 文艺 · 美食 · 高消费",
    27: "🎢 游乐 · 刺激 · 高消费", 28: "🌸 樱花 · 拍照 · 低消费",
    29: "🏫 校园 · 拍照 · 免费", 30: "🌊 江景 · 公园 · 免费",
}


def load_survey_paths():
    """从CSV加载问卷路径数据"""
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "问卷数据.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "问卷数据.csv")
    if not os.path.exists(csv_path):
        return []
    paths = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            paths.append(row["path_code"])
    return paths


def compute_recommendation(j1_yes, j2_yes, survey_paths):
    """实时计算推荐概率"""
    N = len(survey_paths)
    if N == 0:
        return None, 0, {}
    path_counts = Counter(survey_paths)

    path_priors = {p: (path_counts.get(p, 0) + 1) / (N + 32) for p in PATH_MAPPING}

    prefix = ("B" if j1_yes else "A") + "-" + ("B" if j2_yes else "A")
    matching = [p for p in PATH_MAPPING if p.startswith(prefix)]
    total = sum(path_priors[p] for p in matching)
    path_conds = {p: path_priors[p] / total for p in matching}

    item_scores = {}
    for p in matching:
        items = PATH_MAPPING[p]
        raw = {iid: 1.0 / (rank + 1) for rank, iid in enumerate(items)}
        w_sum = sum(raw.values())
        for iid, w in raw.items():
            item_scores[iid] = item_scores.get(iid, 0) + path_conds[p] * w / w_sum

    sorted_items = sorted(item_scores.items(), key=lambda x: x[1], reverse=True)
    best_id, best_prob = sorted_items[0]
    return best_id, best_prob, dict(sorted_items)


def log_click(j1, j2, item_name, prob, clicked):
    """记录点击数据到数据库"""
    conn = get_connection()
    conn.execute(
        "INSERT INTO click_logs (timestamp, j1, j2, recommended_item, recommended_prob, clicked) VALUES (?,?,?,?,?,?)",
        (datetime.now().isoformat(), j1, j2, item_name, prob, clicked)
    )
    conn.commit()
    conn.close()


# ========== 主界面 ==========

if st.session_state.get("rec_submitted"):
    st.success("感谢参与验证！你的反馈已记录。")
    st.info("刷新页面可重新参与。")
    st.stop()

j1 = st.radio(
    "**你今天想去远一点的地方吗？**（单程超过40分钟）",
    ["是", "否"], index=None, horizontal=True, key="j1"
)

j2 = st.radio(
    "**你今天想进行需要体力的活动吗？**（如爬山、骑行、逛游乐场）",
    ["是", "否"], index=None, horizontal=True, key="j2"
)

if j1 is None or j2 is None:
    st.info("👆 请回答以上两个问题")
    st.stop()

st.divider()

survey_paths = load_survey_paths()
if not survey_paths:
    st.error("未找到问卷数据文件（问卷数据.csv）")
    st.stop()

best_id, best_prob, all_scores = compute_recommendation(
    j1 == "是", j2 == "是", survey_paths
)

if best_id is None:
    st.error("计算推荐失败")
    st.stop()

best_name = ITEM_NAMES[best_id]
best_tags = ITEM_TAGS[best_id]

st.markdown("### 为你推荐")
st.markdown(f"""
<div style="border: 2px solid #4FC3F7; border-radius: 12px; padding: 24px;
            background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            text-align: center; margin: 16px 0;">
    <h2 style="margin: 0 0 8px 0; color: #1565C0;">{best_name}</h2>
    <p style="margin: 0 0 12px 0; font-size: 16px; color: #555;">{best_tags}</p>
    <p style="margin: 0; font-size: 14px; color: #888;">推荐置信度: {best_prob*100:.1f}%</p>
</div>
""", unsafe_allow_html=True)

st.markdown("")
st.markdown("**你对这个推荐感兴趣吗？**")

col1, col2 = st.columns(2)
with col1:
    if st.button("✅ 想去！", type="primary", use_container_width=True):
        log_click(j1, j2, best_name, best_prob, 1)
        st.session_state["rec_submitted"] = True
        st.balloons()
        st.rerun()
with col2:
    if st.button("❌ 不感兴趣", use_container_width=True):
        log_click(j1, j2, best_name, best_prob, 0)
        st.session_state["rec_submitted"] = True
        st.rerun()

with st.expander("查看完整推荐排名（Top 10）"):
    for rank, (iid, prob) in enumerate(list(all_scores.items())[:10], 1):
        name = ITEM_NAMES.get(iid, f"项目{iid}")
        bar_len = int(prob / best_prob * 20)
        st.write(f"{rank}. {name}  {'█' * bar_len} {prob*100:.1f}%")
