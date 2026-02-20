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

# 自動算桌次邏輯
def calculate_table(ticket_number):
    try:
        return (int(ticket_number) - 1) // 10 + 1
    except:
        return 0

# --- 2. 繪製地圖函數 (支援橫跨全排樣式) ---
def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error(f"❌ 找不到佈局檔案: {LAYOUT_FILE}")
        return

    df_map = pd.read_csv(LAYOUT_FILE, header=None)
    st.markdown("### 🏟️ 場地實景佈局圖")
    
    for r_idx, row in df_map.iterrows():
        # 先檢查這整列是否包含「舞台」或「入口」
        row_str = "".join([str(v) for v in row if not pd.isna(v)])
        
        if "舞台" in row_str:
            st.markdown("""
                <div style='background-color:#FF4B4B; color:white; text-align:center; 
                padding:15px; border-radius:10px; font-weight:bold; font-size:24px; 
                margin: 10px 0; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);'>
                🎭 舞 臺 STAGE (在此對齊全場)
                </div>
            """, unsafe_allow_html=True)
            continue # 跳過該列的其餘欄位處理
            
        elif "入口" in row_str:
            st.markdown("""
                <div style='background-color