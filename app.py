import streamlit as st
import pandas as pd
import os

# --- 1. 檔案與雲端連結設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
# 根據您提供的連結轉換出的 CSV 下載網址
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="宴會桌次實景系統", page_icon="🎟️", layout="wide")

# 讀取 Google 試算表資料
@st.cache_data(ttl=30) # 每 30 秒自動更新一次
def load_cloud_data():
    try:
        # 強制指定編碼以防亂碼
        return pd.read_csv(SHEET_URL)
    except Exception as e:
        return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

df_guest = load_cloud_data()

# 自動算桌次邏輯
def calculate_table(ticket_number):
    try:
        return (int(ticket_number) - 1) // 10 + 1
    except:
        return 0

# --- 2. 繪製地圖函數 (美化版) ---
def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error(f"❌ 找不到佈局檔案: {LAYOUT_FILE}")
        return

    df_map = pd.read_csv(LAYOUT_FILE, header=None)
    st.markdown("### 🏟️ 場地實景佈局圖")
    
    for r_idx, row in df_map.iterrows():
        row_content = "".join([str(v) for v in row if not pd.isna(v)])
        
        # 橫跨全排的標籤樣式
        if "舞台" in row_content:
            st.markdown("<div style='background-color:#FF4B4B; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold; font-size:24px; margin: 10px 0;'>🚩 舞 臺 STAGE</div>", unsafe_allow_html=True)
            continue
        elif "入口" in row_content:
            st.markdown("<div style='background-color:#2E7D32; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold; font-size:24px; margin: 10px 0;'>🚪 主 入 口 ENTRANCE</div>", unsafe_allow_html=True)
            continue

        cols = st.columns(10) 
        for c_idx, val in enumerate(row):
            if c_idx >= 10: