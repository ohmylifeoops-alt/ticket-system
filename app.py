import streamlit as st
import pandas as pd
import os

# --- 1. 設定與初始化 ---
FILE_NAME = 'guest_data.csv'
st.set_page_config(page_title="票號桌次地圖系統", page_icon="🎟️", layout="wide")

# 讀取資料庫
if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
else:
    df = pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

# 核心邏輯：計算桌次
def calculate_table(ticket_number):
    return (int(ticket_number) - 1) // 10 + 1

# --- 2. 繪製地圖的函數 (定義) ---
def draw_seating_chart(highlighted_tables):
    # 內部輔助函數：畫桌子按鈕
    def draw_btn(num):
        is_active = num in highlighted_tables
        # 增加唯一 key 避免報錯，並根據搜尋狀態變色
        st.button(f"{num}", key=f"map_btn_{num}", type="primary" if is_active else "secondary", use_container_width=True)

    # A. 舞台區 (1-100號)
    st.markdown("<h2 style='text-align: center; color: red; background-color: #fff0f0; padding: 10px; border-radius: 10px;'>🚩 舞台位置 🚩</h2>", unsafe_allow_html=True)
    
    # 核心三桌 (習俗排列：左3 中1 右2)
    st.write("### 舞台正前方 (第一排)")
    c1, c2, c3 = st.columns(3)
    with c1: draw_btn(3)
    with c2: draw_btn(1)
    with c3: draw_btn(2)

    # 4-100號 網格 (每排 5 桌，手機顯示最穩定)
    st.write("### 舞台大區 (4 - 100 號)")
    remaining_100 = list(range(4, 101))
    for i in range(0, len(remaining_100), 5):
        cols = st.columns(5)
        batch = remaining_100[i:i+5]
        for idx, num