"""推荐App页面 - 两个判断题 + 推荐结果"""
import streamlit as st
import sqlite3
import json
import os

DB_PATH = "survey.db"
RESULTS_PATH = "results/probabilities.json"

st.set_page_config(page_title="华科出游推荐", page_icon="🎯")
st.title("🎯 今天去哪儿玩？")
st.caption("回答两个问题，为你推荐最合适的出游目的地")
st.divider()


def load_recommendations():
    if not os.path.exists(RESULTS_PATH):
        return None
    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_item_info(item_id):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT * FROM items WHERE item_id = ?", (item_id,)
    ).fetchone()
    conn.close()
    if row:
        return {
            "id": row[0], "name": row[1], "distance": row[2],
            "energy": row[3], "category": row[4],
            "cost": row[5], "tags": json.loads(row[6])
        }
    return None


def find_best_item(j1, j2, recommendations):
    j1_str = "是" if j1 else "否"
    j2_str = "是" if j2 else "否"
    key = f"recommend_J1={j1_str},J2={j2_str}"
    if key in recommendations:
        rec = recommendations[key]
        best_name = list(rec.keys())[0]
        best_prob = list(rec.values())[0]
        return best_name, best_prob, rec
    return None, None, None


# 判断题
j1 = st.radio(
    "**你今天想去远一点的地方吗？**（单程超过40分钟）",
    ["是", "否"],
    index=None,
    horizontal=True,
    key="j1"
)

j2 = st.radio(
    "**你今天想进行需要体力的活动吗？**（如爬山、骑行、逛游乐场）",
    ["是", "否"],
    index=None,
    horizontal=True,
    key="j2"
)

if j1 is None or j2 is None:
    st.info("👆 请回答以上两个问题")
    st.stop()

st.divider()

# 加载推荐结果
recommendations = load_recommendations()

if recommendations is None:
    st.error("⚠️ 还没有运行数据分析！请先运行 `python analysis.py`")
    st.stop()

# 获取推荐
best_name, best_prob, all_probs = find_best_item(
    j1 == "是", j2 == "是", recommendations
)

if best_name:
    st.subheader(f"为你推荐：{best_name}")
    st.metric("推荐置信度", f"{best_prob * 100:.1f}%")

    st.markdown(f"""
    > **你今天想去{best_name}吗？**
    > 是否愿意点击页面查看更多信息？
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 了解更多", type="primary",
                      use_container_width=True):
            st.success("太好了！推荐成功 🎉")
    with col2:
        if st.button("❌ 划过", use_container_width=True):
            st.info("没关系，下次再来！")

    with st.expander("查看完整推荐排名"):
        for rank, (name, prob) in enumerate(all_probs.items(), 1):
            st.write(f"{rank}. {name}: {prob*100:.1f}%")
            if rank >= 10:
                st.write("...")
                break
