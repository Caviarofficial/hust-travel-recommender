"""动态问卷页面 - 给同学们填写"""
import streamlit as st
from datetime import datetime
from db_utils import get_connection

st.set_page_config(page_title="华科出游推荐问卷", page_icon="🗺️")
st.title("🗺️ 华科周末出游推荐问卷")
st.caption("只需回答5个问题，帮助我们为你推荐最合适的出游目的地！")
st.divider()

# ========== 第1层：所有人回答 ==========
q1 = st.radio(
    "**Q1：今天想走多远？**",
    ["A. 就近逛逛（光谷/校内周边，30分钟内）",
     "B. 出去探索（愿意跨区，40分钟以上）"],
    index=None,
    key="q1"
)

if q1 is None:
    st.info("👆 请从第1题开始作答")
    st.stop()

q1_val = q1[0]

# ========== 第2层：根据Q1分支 ==========
st.divider()
if q1_val == "A":
    q2 = st.radio(
        "**Q2：今天的精力状态如何？**",
        ["A. 想放松（安静、慢节奏、不想太累）",
         "B. 精力充沛（想动起来、找刺激）"],
        index=None, key="q2"
    )
else:
    q2 = st.radio(
        "**Q2：出远门最想做什么？**",
        ["A. 看风景/长见识（文化、历史、自然、艺术）",
         "B. 吃喝玩乐（美食、购物、游乐场）"],
        index=None, key="q2"
    )

if q2 is None:
    st.stop()
q2_val = q2[0]

# ========== 第3层：根据Q1+Q2分支 ==========
st.divider()
branch_2 = f"{q1_val}-{q2_val}"

q3_options = {
    "A-A": ("**Q3：想待在什么样的环境里？**",
            ["A. 户外透气（公园、湖边、绿道）",
             "B. 室内舒适（咖啡馆、书店、展厅）"]),
    "A-B": ("**Q3：想怎么『动』起来？**",
            ["A. 体育运动（骑行、球类、徒步）",
             "B. 娱乐社交（密室、剧本杀、逛街聚餐）"]),
    "B-A": ("**Q3：更想看什么？**",
            ["A. 历史与建筑（古迹、老街、大学校园）",
             "B. 自然与艺术（江景、公园、美术馆/博物馆）"]),
    "B-B": ("**Q3：今天的重点是？**",
            ["A. 美食探店（找好吃的，逛美食街）",
             "B. 购物/游乐（逛商场或去游乐场）"]),
}

q3_title, q3_opts = q3_options[branch_2]
q3 = st.radio(q3_title, q3_opts, index=None, key="q3")

if q3 is None:
    st.stop()
q3_val = q3[0]

# ========== 第4层：根据Q1+Q2+Q3分支 ==========
st.divider()
branch_3 = f"{q1_val}-{q2_val}-{q3_val}"

q4_options = {
    "A-A-A": ("**Q4：今天和几个人一起？**",
              ["A. 独处或1-2人", "B. 3人以上"]),
    "A-A-B": ("**Q4：更想做什么？**",
              ["A. 看书/看展（文艺、知识类）",
               "B. 喝咖啡/甜品（消费享受型）"]),
    "A-B-A": ("**Q4：想要多大运动量？**",
              ["A. 中等（骑行、快走）", "B. 高强度（爬山、球赛）"]),
    "A-B-B": ("**Q4：更想玩什么？**",
              ["A. 沉浸体验（密室逃脱、剧本杀）",
               "B. 逛街聚餐（商场、餐厅）"]),
    "B-A-A": ("**Q4：今天想怎么逛？**",
              ["A. 深度游一个地方", "B. 特种兵多点打卡"]),
    "B-A-B": ("**Q4：更偏向哪种？**",
              ["A. 自然风景（江滩、花园）",
               "B. 艺术展览（美术馆、博物馆）"]),
    "B-B-A": ("**Q4：想吃什么风格？**",
              ["A. 街头小吃/地道老店", "B. 商圈餐厅/网红店"]),
    "B-B-B": ("**Q4：更想去？**",
              ["A. 逛街购物（步行街、商场）",
               "B. 游乐场/刺激项目"]),
}

q4_title, q4_opts = q4_options[branch_3]
q4 = st.radio(q4_title, q4_opts, index=None, key="q4")

if q4 is None:
    st.stop()
q4_val = q4[0]

# ========== 第5层：预算/时间确认 ==========
st.divider()
path_code = f"{q1_val}-{q2_val}-{q3_val}-{q4_val}"

free_paths = ["A-A-A-A", "A-A-A-B", "A-B-A-A", "B-A-B-A", "B-A-A-A"]
if path_code in free_paths:
    q5 = st.radio(
        "**Q5：打算玩多久？**",
        ["A. 半天以内（2-3小时）", "B. 一整天"],
        index=None, key="q5"
    )
else:
    q5 = st.radio(
        "**Q5：今天愿意花多少钱（不含餐饮）？**",
        ["A. 尽量免费（0-30元）", "B. 可以花点（50-200元）"],
        index=None, key="q5"
    )

if q5 is None:
    st.stop()
q5_val = q5[0]

# ========== 提交 ==========
st.divider()
st.success("✅ 所有问题已回答完毕！")
st.write(f"你的路径：**{path_code}-{q5_val}**")

if st.button("📮 提交问卷", type="primary", use_container_width=True):
    conn = get_connection()
    conn.execute(
        "INSERT INTO responses (timestamp, q1, q2, q3, q4, q5, path_code) VALUES (?,?,?,?,?,?,?)",
        (datetime.now().isoformat(), q1_val, q2_val, q3_val, q4_val, q5_val, path_code)
    )
    conn.commit()
    conn.close()
    st.balloons()
    st.success("🎉 提交成功！感谢你的参与！")
