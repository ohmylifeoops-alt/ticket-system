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

# --- 2. 繪製地圖的函數 ---
def draw_seating_chart(highlighted_tables):
    def draw_btn(num):
        is_active = num in highlighted_tables
        st.button(f"{num}", key=f"map_btn_{num}", type="primary" if is_active else "secondary", use_container_width=True)

    st.markdown("<h2 style='text-align: center; color: red; background-color: #fff0f0; padding: 10px; border-radius: 10px;'>🚩 舞台位置 🚩</h2>", unsafe_allow_html=True)
    
    # 第一排：按照您的順序 10 9 8 7 3 1 2 4 5 6
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

    st.markdown("<div style='text-align: center; padding: 15px; border: 2px dashed #999; margin: 20px 0;'>📺 走道 / 電視牆 / 看板區域 📺</div>", unsafe_allow_html=True)

    # 101-170 號
    st.write("### 中間與入口區域 (101 - 170 號)")
    for i in range(101, 171, 10):
        cols = st.columns(10)
        for j in range(10):
            num = i + j
            if num <= 170:
                with cols[j]:
                    draw_btn(num)
    
    st.markdown("<h3 style='text-align: center;'>🚪 入口方向</h3>", unsafe_allow_html=True)

# --- 3. 介面主要內容 ---
st.title("🎟️ 票務登記與桌次視覺化系統")
tab1, tab2, tab3 = st.tabs(["🔍 桌次地圖搜尋", "📝 新增賓客登記", "📊 所有數據管理"])

with tab1: