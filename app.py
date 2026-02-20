import streamlit as st
import pandas as pd
import os

# --- 1. 初始化與檔案讀取 ---
FILE_NAME = 'guest_data.csv'
st.set_page_config(page_title="宴會桌次實景系統", page_icon="🎟️", layout="wide")

if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
else:
    df = pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

def calculate_table(ticket_number):
    return (int(ticket_number) - 1) // 10 + 1

# --- 2. 繪製地圖函數 (確保所有字串與縮排正確) ---
def draw_seating_chart(highlighted_tables):
    def draw_btn(num):
        is_active = num in highlighted_tables
        st.button(f"{num}", key=f"map_btn_{num}", type="primary" if is_active else "secondary", use_container_width=True)

    # === A. 舞台核心區 (1-100號) ===
    st.markdown("<h2 style='text-align: center; color: white; background-color: #d32f2f; padding: 10px; border-radius: 10px;'>🚩 舞台 STAGE 🚩</h2>", unsafe_allow_html=True)
    
    st.write("⬅️ 上菜方向 | 舞台第一排 (核心排序)")
    row1_order = [10, 9, 8, 7, 3, 1, 2, 4, 5, 6]
    cols1 = st.columns(10)
    for idx, num in enumerate(row1_order):
        with cols1[idx]:
            draw_btn(num)

    st.write("---")
    st.caption("30尺龍帳區 (11 - 100 號)")
    for i in range(11, 101, 10):
        # 走道標示：每兩排(20桌)