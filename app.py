import streamlit as st
import pandas as pd
import os

# --- 1. 初始化與檔案設定 ---
GUEST_FILE = 'guest_data.csv'
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv'

st.set_page_config(page_title="宴會桌次實景系統", page_icon="🎟️", layout="wide")

# 讀取賓客資料庫
if os.path.exists(GUEST_FILE):
    df_guest = pd.read_csv(GUEST_FILE)
else:
    df_guest = pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

# 自動算桌次邏輯：票號每 10 人一桌
def calculate_table(ticket_number):
    try:
        # 確保票號為整數後進行計算
        return (int(ticket_number) - 1) // 10 + 1
    except:
        return 0

# --- 2. 繪製地圖函數 (完全遵循您的 Excel 佈局) ---
def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error(f"找不到佈局檔案: {LAYOUT_FILE}，請確保此 CSV 檔已上傳至 GitHub。")
        return

    # 讀取 Excel 網格數據
    df_map = pd.read_csv(LAYOUT_FILE, header=None)

    st.markdown("### 🏟️ 場地實景佈局圖")
    
    # 逐列(Row)掃描 Excel 格子
    for r_idx, row in df_map.iterrows():
        cols = st.columns(10) 
        for c_idx, val in enumerate(row):
            if c_idx >= 10: break 
            
            with cols[c_idx]:
                # 處理空位
                if pd.isna(val) or str(val).strip() == "":
                    st.write("")
                # 處理標籤：舞台
                elif str(val).strip() == "舞台":
                    st.markdown("<div style='background-color:#d32f2f; color:white; text-align:center; padding:5px; border-radius:5px; font-weight:bold; font-size:12px;'>舞台</div>", unsafe_allow_html=True)
                # 處理標籤：電視
                elif str(val).strip() == "電視":
                    st.markdown("<div style='background-color:#333; color:white; text-align:center; padding:5px; border-radius:5px; font-size:12px;'>📺</div>", unsafe_allow_html=True)
                # 處理桌號按鈕
                else:
                    try:
                        table_num = int(float(val))
                        is_active = table_num in highlighted_tables
                        # 使用唯一 key 避免按鈕衝突
                        st.button(