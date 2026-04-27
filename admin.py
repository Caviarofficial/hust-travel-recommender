"""数据管理页面 - 查看和导出问卷数据"""
import streamlit as st
import pandas as pd
from db_utils import get_connection

st.set_page_config(page_title="数据管理", page_icon="📊")
st.title("📊 问卷数据管理")

conn = get_connection()

# 基本统计
total = conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
st.metric("已收集问卷数", total)

if total > 0:
    st.divider()

    # 所有记录
    st.subheader("全部问卷记录")
    df = pd.read_sql("SELECT * FROM responses ORDER BY id DESC", conn)
    st.dataframe(df, use_container_width=True)

    # 路径分布
    st.subheader("路径分布")
    path_df = pd.read_sql(
        "SELECT path_code, COUNT(*) as count FROM responses "
        "GROUP BY path_code ORDER BY count DESC", conn
    )
    st.bar_chart(path_df.set_index("path_code"))

    # 导出 CSV
    st.subheader("导出数据")
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("下载 CSV", csv, "survey_data.csv", "text/csv")

    # 删除记录
    st.subheader("删除记录")
    del_id = st.number_input("输入要删除的记录 ID", min_value=1, step=1)
    if st.button("删除", type="secondary"):
        conn.execute("DELETE FROM responses WHERE id = ?", (del_id,))
        conn.commit()
        st.success(f"已删除 id={del_id} 的记录")
        st.rerun()
else:
    st.info("暂无数据，等待同学填写问卷。")

conn.close()
