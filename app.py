import streamlit as st
import pandas as pd
import os

# --- 1. 設定與初始化 ---
FILE_NAME = 'guest_data.csv'
st.set_page_config(page_title="票號桌次管理與地圖系統", page_icon="🎟️", layout="wide")

# 讀取資料庫
if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
else:
    df = pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

# 核心邏輯：計算桌次
def calculate_table(ticket_number):
    return (int(ticket_number) - 1) // 10 + 1

# --- 2. 繪製地圖的函數 ---
def draw_seating_chart(highlighted_tables):
    def draw_btn(num):
        is_active = num in highlighted_tables
        st.button(f"{num}", key=f"map_btn_{num}", type="primary" if is_active else "secondary", use_container_width=True)

    # --- A. 舞台核心區 (1-100號) ---
    st.markdown("<h2 style='text-align: center; color: red; background-color: #fff0f0; padding: 10px; border-radius: 10px;'>🚩 舞台位置 🚩</h2>", unsafe_allow_html=True)
    
    # 舞台第一排：精確排序 10 9 8 7 3 1 2 4 5 6
    st.write("### 舞台第一排")
    row1 = [10, 9, 8, 7, 3, 1, 2, 4, 5, 6]
    cols1 = st.columns(10)
    for idx, num in enumerate(row1):
        with cols1[idx]:
            draw_btn(num)

    # 11-100 號：每排 10 桌
    st.write("### 舞台大區 (11 - 100 號)")
    for i in range(11, 101, 10):
        cols = st.columns(10)
        for j in range(10):
            num = i + j
            if num <= 100:
                with cols[j]:
                    draw_btn(num)

    # 走道與空間標示：電視牆
    st.markdown("<div style='text-align: center; padding: 15px; border: 2px dashed #999; margin: 20px 0;'>📺 電視牆 / 看板區域 📺</div>", unsafe_allow_html=True)

    # --- B. 電視牆後第一階段 (101-125 號)：採 5 欄排法 ---
    st.write("### 電視牆後 (101 - 125 號)")
    area_25 = list(range(101, 126))
    for i in range(0, len(area_25), 5):
        cols = st.columns(5)
        batch = area_25[i:i+5]
        for idx, num in enumerate(batch):
            with cols[idx]:
                draw_btn(num)

    # --- C. 電視牆後第二階段 (126-170 號)：採 10 欄排法 ---
    st.write("### 入口前大區 (126 - 170 號)")
    area_rest = list(range(126, 171))
    for i in range(0, len(area_rest), 10):
        cols = st.columns(10)
        batch = area_rest[i:i+10]
        for idx, num in enumerate(batch):
            with cols[idx]:
                draw_btn(num)
    
    st.markdown("<h3 style='text-align: center;'>🚪 入口方向</h3>", unsafe_allow_html=True)

# --- 3. 介面主要內容 ---
st.title("🎟️ 票務登記與桌次視覺化系統")
tab1, tab2, tab3 = st.tabs(["🔍 桌次地圖搜尋", "📝 新增賓客登記", "📊 所有數據管理"])

with tab1:
    search_term = st.text_input("🔍 搜尋姓名、電話、票號或售出者：", key="search_box")
    highlighted = []
    if search_term:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
        highlighted = df[mask]['桌號'].tolist()
        if highlighted:
            st.success(f"找到相關賓客，位於第 {list(set(highlighted))} 桌")
    draw_seating_chart(highlighted)

with tab2:
    with st.form("my_form", clear_on_submit=True):
        n = st.text_input("姓名")
        t = st.number_input("票號", min_value=1, max_value=2000, step=1)
        p = st.text_input("聯絡電話")
        s = st.text_input("售出者")
        if st.form_submit_button("提交登記"):
            if n:
                tbl = calculate_table(t)
                new_row = pd.DataFrame({"姓名":[n],"聯絡電話":[p],"票號":[t],"售出者":[s],"桌號":[tbl]})
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(FILE_NAME, index=False)
                st.success(f"✅ 登記成功！{n} 分配在第 {tbl} 桌")
            else:
                st.warning("請輸入姓名")

with tab3:
    st.subheader("完整名單清單")
    st.dataframe(df.sort_values(by="桌號"), use_container_width=True)