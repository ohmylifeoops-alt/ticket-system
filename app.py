import streamlit as st
import pandas as pd
import os

# --- 1. 設定與初始化 ---
FILE_NAME = 'guest_data.csv'
st.set_page_config(page_title="票號桌次管理與地圖系統", page_icon="🎟️", layout="wide")

if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
else:
    df = pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

def calculate_table(ticket_number):
    return (int(ticket_number) - 1) // 10 + 1

# --- 2. 繪製地圖函數 ---
def draw_seating_chart(highlighted_tables):
    def draw_btn(num):
        is_active = num in highlighted_tables
        st.button(f"{num}", key=f"map_btn_{num}", type="primary" if is_active else "secondary", use_container_width=True)

    # --- A. 舞台核心區 (1-100號) ---
    st.markdown("<h2 style='text-align: center; color: red; background-color: #fff0f0; padding: 10px; border-radius: 10px;'>🚩 舞台位置 🚩</h2>", unsafe_allow_html=True)
    
    # 第一排：完全依照您的指定順序
    st.write("### 舞台第一排 (核心位)")
    row1_order = [10, 9, 8, 7, 3, 1, 2, 4, 5, 6]
    cols1 = st.columns(10)
    for idx, num in enumerate(row1_order):
        with cols1[idx]:
            draw_btn(num)

    # 11-100 號：每排 10 桌
    st.write("### 核心大區 (11 - 100 號)")
    remaining_100 = list(range(11, 101))
    for i in range(0, len(remaining_100), 10):
        cols = st.columns(10)
        batch = remaining_100[i:i+10]
        for idx, num in enumerate(batch):
            with cols[idx]:
                draw_btn(num)

    # 走道分隔
    st.markdown("<div style='text-align: center; padding: 15px; border: 2px dashed #999; margin: 20px 0;'>📺 走道 / 電視牆 / 看板區域 📺</div>", unsafe_allow_html=True)

    # --- B. 中間與入口區 (101-170號) ---
    # 中間區 101-140
    st.write("### 中間與入口區域 (101 - 170 號)")
    all_rest = list(range(101, 171))
    for i in range(0, len(all_rest), 10):
        cols = st.columns(10)
        batch = all_rest[i:i+10]
        for idx, num in enumerate(batch):
            with cols[idx]:
                draw_btn(num)
    
    st.markdown("<h3 style='text-align: center;'>🚪 入口方向</h3>", unsafe_allow_html=True)

# --- 3. 介面內容 ---
st.title("🎟️ 票務系統與實景桌次圖")
tab1, tab2, tab3 = st.tabs(["🔍 桌次搜尋", "📝 新增登記", "📊 管理"])

with tab1:
    search_term = st.text_input("🔍 搜尋姓名、電話、票號或售出者：")
    highlighted = []
    if search_term:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
        highlighted = df[mask]['桌號'].tolist()
        if highlighted:
            st.success(f"找到賓客，位於第 {list(set(highlighted))} 桌")
    
    draw_seating_chart(highlighted)

with tab2: # 原有登記邏輯
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("姓名")
            ticket = st.number_input("票號", min_value=1, max_value=2000,