import streamlit as st
import pandas as pd
import os

# --- 1. 初始化與檔案設定 ---
GUEST_FILE = 'guest_data.csv'
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv'  # 這是您上傳的佈局檔名

st.set_page_config(page_title="宴會桌次實景系統", page_icon="🎟️", layout="wide")

# 讀取賓客資料庫
if os.path.exists(GUEST_FILE):
    df_guest = pd.read_csv(GUEST_FILE)
else:
    df_guest = pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

# 自動算桌次邏輯 (票號每 10 號一桌)
def calculate_table(ticket_number):
    return (int(ticket_number) - 1) // 10 + 1

# --- 2. 繪製地圖函數 (地毯式檢查：完全遵循 Excel 網格) ---
def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error(f"找不到佈局檔案: {LAYOUT_FILE}，請確保檔案已上傳至 GitHub。")
        return

    # 讀取 Excel 網格 (不設 header 以獲取原始座標)
    df_map = pd.read_csv(LAYOUT_FILE, header=None)

    st.markdown("### 🏟️ 場地實景佈局圖")
    
    # 逐列(Row)掃描 Excel 格子
    for r_idx, row in df_map.iterrows():
        cols = st.columns(10)  # 固定 10 欄以對應 Excel 寬度
        for c_idx, val in enumerate(row):
            if c_idx >= 10: break # 防止超出寬度
            
            with cols[c_idx]:
                # 處理空位
                if pd.isna(val) or str(val).strip() == "":
                    st.write