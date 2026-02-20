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

# 核心邏輯：計算桌次 (每10號一桌)
def calculate_table(ticket_number):
    return (int(ticket_number) - 1) // 10 + 1

# --- 2. 繪製地圖的函數 ---
def draw_seating_chart(highlighted_tables):
    def draw_btn(num):
        is_active = num in highlighted_tables
        st.button(f"{num}", key=f"map_btn_{num}", type="primary" if is_active else "secondary", use_container_width=True)

    # A. 舞台核心區 (1-100號)
    st.markdown("<h2 style='text-align: center; color: red; background-color: #fff0f0; padding: 10px; border-radius: 10px;'>🚩 舞台位置 🚩</h2>", unsafe_allow_html=True)
    
    # 舞台第一排 (核心位：左3 中1 右2)
    st.write("### 舞台正前方第一排")
    c1, c2, c3 = st.columns(3)
    with c1: draw_btn(3)
    with c2: draw_btn(1)
    with c3: draw_btn(2)

    # 4-100號 網格
    st.write("### 舞台大區 (4 - 100 號)")
    remaining_100 = list(range(4, 101))
    for i in range(0, len(remaining_100), 5):
        cols = st.columns(5)
        batch = remaining_100[i:i+5]
        for idx, num in enumerate(batch): # 修正處：加入了 'in'
            with cols[idx]:
                draw_btn(num)

    # 走道與看板空間
    st.markdown("<div style='text-align: center; padding: 15px; border: 2px dashed #999; margin: 20px 0;'>📺 走道 / 電視牆 / 看板區域 📺</div>", unsafe_allow_html=True)

    # B. 中間區 (101-140號)
    st.write("### 中間區域 (101 - 140 號)")
    area_40 = list(range(101, 141))
    for i in range(0, len(area_40), 5):
        cols = st.columns(5)
        batch = area_40[i:i+5]
        for idx, num in enumerate(batch):
            with cols[idx]:
                draw_btn(num)

    # C. 入口區 (141-170號)
    st.write("### 入口區域 (141 - 170 號)")
    area_30 = list(range(141, 171))
    for i in range(0, len(area_30), 5):
        cols = st.columns(5)
        batch = area_30[i:i+5]
        for idx, num in enumerate(batch):
            with cols[idx]:
                draw_btn(num)
    
    st.markdown("<h3 style='text-align: center;'>🚪 入口方向</h3>", unsafe_allow_html=True)

# --- 3. 介面主要內容 ---
st.title("🎟️ 票務登記與桌次視覺化系統")
tab1, tab2, tab3 = st.tabs(["🔍 桌次地圖搜尋", "📝 新增賓客登記", "📊 所有數據管理"])

# 功能一：地圖搜尋
with tab1:
    search_term = st.text_input("🔍 搜尋姓名、電話、票號或售出者：")
    highlighted = []
    if search_term:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
        highlighted = df[mask]['桌號'].tolist()
        if highlighted:
            st.success(f"找到相關賓客，位於第 {list(set(highlighted))} 桌")
    
    draw_seating_chart(highlighted)

# 功能二：新增資料 (保留原本邏輯)
with tab2:
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("姓名")
            ticket = st.number_input("票號 (1-2000)", min_value=1, max_value=2000, step=1)
        with col2:
            phone = st.text_input("聯絡電話")
            seller = st.text_input("售出者")
            
        submitted = st.form_submit_button("新增並自動分配桌次")
        if submitted:
            if not df.empty and ticket in df['票號'].values:
                st.error(f"錯誤：票號 {ticket} 已被登記！")
            elif not name:
                st.warning("請輸入姓名")
            else:
                table_num = calculate_table(ticket)
                new_row = pd.DataFrame({"姓名": [name], "聯絡電話": [phone], "票號": [ticket], "售出者": [seller], "桌號": [table_num]})
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(FILE_NAME, index=False)
                st.success(f"✅ 已新增！{name} 分配在第 {table_num} 桌")

# 功能三：數據管理
with tab3:
    st.subheader("完整賓客名單")
    st.dataframe(df.sort_values(by="桌號"), use_container_width=True)