"""数据管理页面 - 查看问卷数据 + 验证统计"""
import streamlit as st
import pandas as pd
from db_utils import get_connection

st.set_page_config(page_title="数据管理", page_icon="📊")
st.title("📊 数据管理")

tab1, tab2 = st.tabs(["问卷数据", "推荐验证统计"])

conn = get_connection()

with tab1:
    total = conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
    st.metric("已收集问卷数", total)

    if total > 0:
        st.divider()
        st.subheader("全部问卷记录")
        df = pd.read_sql("SELECT * FROM responses ORDER BY id DESC", conn)
        st.dataframe(df, use_container_width=True)

        st.subheader("路径分布")
        path_df = pd.read_sql(
            "SELECT path_code, COUNT(*) as count FROM responses "
            "GROUP BY path_code ORDER BY count DESC", conn
        )
        st.bar_chart(path_df.set_index("path_code"))

        st.subheader("导出数据")
        csv_data = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 下载 CSV", csv_data, "survey_data.csv", "text/csv")
    else:
        st.info("暂无数据，等待同学填写问卷。")

with tab2:
    click_total = conn.execute("SELECT COUNT(*) FROM click_logs").fetchone()[0]
    st.metric("验证总人数", click_total)

    if click_total > 0:
        clicked = conn.execute("SELECT COUNT(*) FROM click_logs WHERE clicked=1").fetchone()[0]
        actual_rate = clicked / click_total

        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("点击人数", clicked)
        with col2:
            st.metric("实际命中率", f"{actual_rate:.1%}")
        with col3:
            st.metric("理论命中率", "30.8%", delta=f"{(actual_rate - 0.308)*100:+.1f}%")

        st.divider()
        st.subheader("各象限命中率")

        theory = {"否-否": 0.3500, "否-是": 0.3158, "是-否": 0.3333, "是-是": 0.2222}
        quad_df = pd.read_sql(
            "SELECT j1, j2, COUNT(*) as total, SUM(clicked) as clicks FROM click_logs GROUP BY j1, j2",
            conn
        )
        for _, row in quad_df.iterrows():
            key = f"{row['j1']}-{row['j2']}"
            rate = row["clicks"] / row["total"] if row["total"] > 0 else 0
            th = theory.get(key, 0)
            label = {"否-否": "近+放松", "否-是": "近+活跃", "是-否": "远+放松", "是-是": "远+活跃"}.get(key, key)
            st.write(f"**J1={row['j1']}, J2={row['j2']}（{label}）**：{int(row['clicks'])}/{int(row['total'])} = {rate:.1%}（理论 {th:.1%}）")

        st.divider()
        st.subheader("验证明细")
        click_df = pd.read_sql("SELECT * FROM click_logs ORDER BY id DESC", conn)
        st.dataframe(click_df, use_container_width=True)

        csv_click = click_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 下载验证数据 CSV", csv_click, "click_logs.csv", "text/csv")
    else:
        st.info("暂无验证数据。请让同学在「出游推荐」页面完成验证。")

conn.close()
