"""主入口 - 推荐验证页面（课堂验证算法命中率）"""
import streamlit as st
import csv
import os
from collections import Counter
from datetime import datetime
from db_utils import get_connection

st.set_page_config(
    page_title="华科出游推荐",
    page_icon="🎯",
    layout="centered"
)

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

ITEM_INFO = {
    1: {"distance": "骑行15分钟 / 公交20分钟", "cost": "30-50元", "type": "湖畔绿道骑行",
        "hook": "全长101公里的东湖绿道是国内最长城市湖泊绿道，磨山段一路可见楚文化雕塑群"},
    2: {"distance": "公交25分钟", "cost": "免费", "type": "湿地观鸟与湖畔漫步",
        "hook": "冬季有大量候鸟栖息，是武汉市区内少有的能近距离观赏野生鸟类的地方"},
    3: {"distance": "校内步行5分钟", "cost": "免费", "type": "校园湖畔休闲散步",
        "hook": "喻家湖是华科的'隐藏海'，湖面面积比很多大学的整个校园还大"},
    4: {"distance": "校内步行即达", "cost": "免费", "type": "校园原生态林地徒步",
        "hook": "华科绿化覆盖率超72%，被称为'森林大学'，校内有成片法国梧桐和水杉林"},
    5: {"distance": "地铁/公交15分钟", "cost": "100-200元", "type": "大型商业步行街",
        "hook": "全长1350米的步行街拥有西班牙、意大利、德国等多国风情街区建筑"},
    6: {"distance": "公交20分钟", "cost": "80-150元", "type": "潮流商圈探店",
        "hook": "武汉年轻人密度最高的商圈，网红店更新极快，被称为'光谷的太古里'"},
    7: {"distance": "地铁20分钟", "cost": "100-200元", "type": "艺术展览+购物融合体验",
        "hook": "每层都有当代艺术装置，逛街如同逛美术馆，拍照出片率极高"},
    8: {"distance": "骑行10分钟", "cost": "30-50元", "type": "精品咖啡与安静空间",
        "hook": "关山大道沿线聚集大量独立咖啡馆，是光谷程序员和大学生的'第二自习室'"},
    9: {"distance": "公交15分钟", "cost": "免费", "type": "独立书店阅读体验",
        "hook": "光谷书房24小时开放，深夜也能找到安静角落，是武汉少有的'不打烊书房'"},
    10: {"distance": "公交40分钟", "cost": "免费", "type": "郊野湿地生态观光",
         "hook": "保留了大片原生芦苇荡，秋天芦花飘飞时宛如进入宫崎骏动画场景"},
    11: {"distance": "公交15分钟", "cost": "80-120元/人", "type": "沉浸式解谜",
         "hook": "光谷密室竞争激烈，不少店家投入百万级实景搭建，机关复杂程度全国排名靠前"},
    12: {"distance": "公交15分钟", "cost": "80-130元/人", "type": "沉浸式角色扮演推理",
         "hook": "武汉是全国剧本杀门店密度最高的城市之一，光谷片区尤其集中，不少是首发城限本"},
    13: {"distance": "公交25分钟", "cost": "50-80元", "type": "网球运动",
         "hook": "曾举办WTA武汉公开赛，李娜退役仪式也在此举行"},
    14: {"distance": "公交30分钟", "cost": "20-40元", "type": "郊野绿道骑行",
         "hook": "沿线有大片花海和湿地，人少景美，是武汉骑行圈公认的'宝藏路线'"},
    15: {"distance": "地铁1站/10分钟", "cost": "60-100元", "type": "聚餐社交",
         "hook": "光谷广场地下转盘是亚洲最大地下交通枢纽，直径200米，三条地铁线交汇"},
    16: {"distance": "地铁50分钟", "cost": "70元门票", "type": "历史名胜登高览胜",
         "hook": "历史上曾被毁重建十余次，堪称'最坚强的楼'，登顶可俯瞰长江两岸全景"},
    17: {"distance": "地铁+步行45分钟", "cost": "50-80元", "type": "文艺老街漫步",
         "hook": "全长1.2公里却藏着50多处百年历史建筑，是武汉近代教育和医疗的发源地"},
    18: {"distance": "地铁+步行45分钟", "cost": "30-60元", "type": "老武汉地道美食街",
         "hook": "赵师傅热干面和大连铁板鱿鱼常年排队，是武汉本地人认证的'过早圣地'"},
    19: {"distance": "地铁60分钟", "cost": "免费", "type": "长江江畔休闲散步",
         "hook": "全长7公里，是亚洲最大城市内陆江滩公园，夜晚灯光秀免费观赏"},
    20: {"distance": "地铁50分钟", "cost": "免费", "type": "长江大桥步行体验",
         "hook": "万里长江第一桥，步行过桥全程1.6公里，体验'一桥飞架南北'的壮阔"},
    21: {"distance": "公交30分钟", "cost": "免费（需预约）", "type": "历史文物参观",
         "hook": "镇馆之宝曾侯乙编钟重达2567公斤，出土时仍能演奏，是世界音乐史上的奇迹"},
    22: {"distance": "地铁55分钟", "cost": "免费", "type": "当代艺术展览",
         "hook": "建筑前身是1930年代的金城银行，本身就是一件优秀的历史建筑作品"},
    23: {"distance": "地铁35分钟", "cost": "100-200元", "type": "滨水商业街",
         "hook": "全长1.5公里的'中国第一条城市水街'，建筑风格横跨民国到现代"},
    24: {"distance": "地铁55分钟", "cost": "50-100元", "type": "武汉顶级夜宵聚集地",
         "hook": "被称为'武汉深夜食堂'，凌晨两点依然人声鼎沸，本地人认证的美食天花板"},
    25: {"distance": "地铁55分钟", "cost": "100-150元", "type": "百年商业步行街",
         "hook": "有'武汉二十世纪建筑博物馆'之称，沿街13栋历史建筑涵盖欧式、罗马式等风格"},
    26: {"distance": "地铁60分钟", "cost": "120-200元", "type": "高端时尚街区",
         "hook": "由上海新天地同一团队打造，老租界建筑与现代设计碰撞，武汉最有'国际范'的街区"},
    27: {"distance": "地铁50分钟", "cost": "200-250元门票", "type": "大型主题游乐园",
         "hook": "'木翼双龙'是亚洲首座双龙木质过山车，全程尖叫不断"},
    28: {"distance": "公交20分钟", "cost": "60元（花季）", "type": "樱花观赏与园林游览",
         "hook": "樱花品种50余个、树木超万株，规模是武大樱花的数十倍，却远没那么拥挤"},
    29: {"distance": "公交25分钟", "cost": "免费（樱花季需预约）", "type": "民国建筑群与校园漫步",
         "hook": "早期建筑群是全国重点文保单位，被称为'中国最美大学校园'"},
    30: {"distance": "地铁55分钟", "cost": "免费", "type": "登山观江与历史遗迹",
         "hook": "海拔仅90米却能同时俯瞰长江和汉江交汇，山上三国古迹让你一秒穿越回赤壁之战"},
}


def load_survey_paths():
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "问卷数据.csv")
    if not os.path.exists(csv_path):
        return []
    paths = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            paths.append(row["path_code"])
    return paths


def compute_recommendation(j1_yes, j2_yes, survey_paths):
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
info = ITEM_INFO[best_id]

st.markdown("### 🎉 根据你的偏好，我们为你找到了最佳去处！")
st.markdown(f"""
<div style="border: 2px solid #4FC3F7; border-radius: 16px; padding: 28px;
            background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            margin: 16px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <h2 style="margin: 0 0 12px 0; color: #1565C0; text-align: center;">{best_name}</h2>
    <p style="margin: 0 0 16px 0; font-size: 15px; color: #555; text-align: center;">{best_tags}</p>
    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
        <tr>
            <td style="padding: 8px 12px; color: #666;">📍 距华科</td>
            <td style="padding: 8px 12px; font-weight: bold;">{info['distance']}</td>
        </tr>
        <tr style="background: rgba(255,255,255,0.5);">
            <td style="padding: 8px 12px; color: #666;">🎯 活动类型</td>
            <td style="padding: 8px 12px; font-weight: bold;">{info['type']}</td>
        </tr>
        <tr>
            <td style="padding: 8px 12px; color: #666;">💰 人均消费</td>
            <td style="padding: 8px 12px; font-weight: bold;">{info['cost']}</td>
        </tr>
    </table>
    <div style="margin-top: 16px; padding: 12px 16px; background: rgba(255,255,255,0.7);
                border-radius: 8px; border-left: 4px solid #FF8F00;">
        <p style="margin: 0; font-size: 14px; color: #333; line-height: 1.6;">
            💡 <b>你知道吗？</b> {info['hook']}
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("")
st.markdown("**这个周末，要不要去试试？**")

col1, col2 = st.columns(2)
with col1:
    if st.button("✅ 感兴趣，想去看看！", type="primary", use_container_width=True):
        log_click(j1, j2, best_name, best_prob, 1)
        st.session_state["rec_submitted"] = True
        st.balloons()
        st.rerun()
with col2:
    if st.button("❌ 这次不太想去", use_container_width=True):
        log_click(j1, j2, best_name, best_prob, 0)
        st.session_state["rec_submitted"] = True
        st.rerun()

with st.expander("查看完整推荐排名（Top 10）"):
    for rank, (iid, prob) in enumerate(list(all_scores.items())[:10], 1):
        name = ITEM_NAMES.get(iid, f"项目{iid}")
        bar_len = int(prob / best_prob * 20)
        st.write(f"{rank}. {name}  {'█' * bar_len} {prob*100:.1f}%")