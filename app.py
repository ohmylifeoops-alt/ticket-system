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

def calculate_table(ticket_number):
    return (int(ticket_number) - 1) // 10 + 1

# --- 2. 繪製地圖的函數 (完全依照手繪圖佈局) ---
def draw_seating_chart(highlighted_tables):
    def draw_btn(num):
        is_active = num in highlighted_tables
        st.button(f"{num}", key=f"map_btn_{num}", type="primary" if is_active else "secondary", use_container_width=True)

    # === A. 舞台核心區 (1-100號) ===
    # 參考 image_c4dd66.jpg: 包含龍帳分區與上菜方向
    st.markdown("<h2 style='text-align: center; color: white; background-color: #d32f2f; padding: 10px; border-radius: 10px;'>舞台 STAGE</h2>", unsafe_allow_html=True)
    
    # 舞台第一排 (核心位)
    st.write("⬅️ 上菜方向 | 舞台第一排")
    row1 = [10, 9, 8, 7, 3, 1, 2, 4, 5, 6]
    cols1 = st.columns(10)
    for idx, num in enumerate(row1):
        with cols1[idx]:
            draw_btn(num)

    # 11-100 號：模擬 30尺龍帳 與 走道
    st.write("---")
    st.caption("30尺龍帳區 (每兩排設一走道)")
    
    tables_stage = list(range(11, 101))
    for r in range(0, len(tables_stage), 10):
        # 模擬手繪圖中的走道感：每兩排加一個間隔
        if r > 0 and r % 20 == 0:
            st.markdown("<div style='margin: 20px 0; border-top: 1px dashed #ccc; text-align: center; color: #999;'>↑ ⬅️ 走道 AISLE ⬅️ ↑</div>", unsafe_allow_html=True)
        
        cols = st.columns(10)
        batch = tables_stage[r : r + 10]
        for idx, num in enumerate(batch):
            with cols[idx]:
                draw_btn(num)

    # === B. 電視牆分界線 ===
    # 參考 image_c4dd82.jpg
    st.markdown("<div style='text-align: center; padding: 30px; background-color: #333; color: white; margin: 30px 0; border-radius: 5px;'>📺 電視牆 & 大型看板 📺</div>", unsafe_allow_html=True)

    # === C. 電視牆後區域 (101-125 號) ===
    # 依照要求：101-125 採 5 欄排法
    st.write("### 📺 電視牆後區 (101 - 125 號)")
    st.caption("⬅️ 上菜方向")
    area_101_125 = list(range(101, 126))
    for i in range(