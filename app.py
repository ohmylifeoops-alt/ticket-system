import streamlit as st
import pandas as pd
import os

# --- 1. 設定與初始化 ---
FILE_NAME = 'guest_data.csv'
st.set_page_config(page_title="宴會桌次實景查詢系統", page_icon="🎟️", layout="wide")

# 讀取資料庫
if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
else:
    df = pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

# 自動算桌次邏輯 (每 10 人一桌)
def calculate_table(ticket_number):
    return (int(ticket_number) - 1) // 10 + 1

# --- 2. 繪製地圖的函數 (完全依照手繪圖與最新指令) ---
def draw_seating_chart(highlighted_tables):
    def draw_btn(num):
        is_active = num in highlighted_tables
        st.button(f"{num}", key=f"map_btn_{num}", type="primary" if is_active else "secondary", use_container_width=True)

    # === A. 舞台核心區 (1-100號) ===
    st.markdown("<h2 style='text-align: center; color: white; background-color: #d32f2f; padding: 10px; border-radius: 10px;'>🚩 舞台 STAGE 🚩</h2>", unsafe_allow_html=True)
    
    # 舞台第一排：按照您要求的 10, 9, 8, 7, 3, 1, 2, 4, 5, 6 順序
    st.write("⬅️ 上菜方向 | 舞台第一排")
    row1 = [10, 9, 8, 7, 3, 1, 2, 4, 5, 6]
    cols1 = st.columns(10)
    for idx, num in enumerate(row1):
        with cols1[idx]:
            draw_btn(num)

    # 11-100 號：每兩排設一橫向走道模擬龍帳
    st.write("---")
    st.caption("30尺龍帳區 (11 - 100 號)")
    for i in range(11, 101, 10):
        # 每兩排(20桌)增加一個走道標示
        if i > 11 and (i - 11) % 20 == 0:
            st.markdown("<div style='text-align: center; color: #999; margin: 15px 0; border-top: 1px dashed #ccc;'>↑ ⬅️ 走道 AISLE ⬅️ ↑</div>", unsafe_allow_html=True)
        
        cols = st.columns(10)
        for j in range(10):
            num = i + j
            if num <= 100:
                with cols[j]:
                    draw_btn(num)

    # === B. 電視牆分界線 ===
    st.markdown("<div style='text-align: center; padding: 20px; background-color: #333; color: white; margin: 30px 0; border-radius: 5px;'>📺 電視牆 &