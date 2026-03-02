import streamlit as st
import pandas as pd
import requests
from io import StringIO
import os
import csv

# --- 1. 系統設定 ---
st.set_page_config(page_title="福慧千人宴", page_icon="🎟️", layout="wide")

# --- 🎨 核心 CSS (美化與佈局) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main-header {
        text-align: center; color: #d32f2f !important; font-size: 38px !important;
        font-weight: 900 !important; margin-bottom: 5px !important; padding-top: 20px !important;
    }
    .sub-header {
        text-align: center; color: #555 !important; font-size: 18px !important; margin-bottom: 25px !important;
    }
    /* 彈窗樣式 */
    .popup-container {
        position: fixed; top: 45%; left: 50%; transform: translate(-50%, -50%);
        width: 350px; background-color: #FFD700; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); z-index: 9999;
        text-align: center; border: 4px solid #DAA520; padding: 30px 20px;
    }
    .close-x { position: absolute; top: 10px; right: 15px; font-size: 24px; font-weight: bold; color: #555; text-decoration: none; }
    /* 地圖標籤 */
    .label-box-fixed {
        background-color: var(--label-color); color: white; text-align: center; padding: 12px !important;
        border-radius: 10px; font-weight: bold; font-size: 22px !important; margin: 15px 0 !important; width: 100%;
    }
    [data-testid="stHorizontalBlock"] { margin-bottom: -18px !important; }
    .stButton > button { height: 2.8em !important; }
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important; border: 2px solid #FBC02D !important; font-weight: bold;
    }
    .target-spot { scroll-margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- 📖 顯示標頭 ---
st.markdown('<div class="main-header">福慧千人宴共築聖德願</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">桌次查詢系統 (線上/線下整合版)</div>', unsafe_allow_html=True)

# --- 🔍 2. 搜尋框 ---
search_q = st.text_input("🔍 搜尋：", placeholder="輸入姓名或票號直接搜尋", key="search_main", label_visibility="collapsed")

# --- 3. 資料庫載入 (雲端 Google Sheets 修復版) ---
@st.cache_data(ttl=60)
def load_data():
    # 這是你的 Google Sheets CSV 網址
    sheet_url = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"
    try:
        # 使用 requests 強制獲取最新資料
        response = requests.get(sheet_url)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            df['票號_str'] = df['票號'].astype(str)
            df['桌號'] = pd.to_numeric(df['桌號'], errors='coerce').fillna(0).astype(int)
            return df
        return None
    except:
        # 雲端失敗時，嘗試讀取本地備份 (線下版)
        if os.path.exists('賓客總表.csv'):
            return pd.read_csv('賓客總表.csv')
        return None

df_guest = load_data()

# --- 4. 查詢邏輯與彈窗 (包含彩蛋與實景跳轉) ---
if search_q:
    if search_q == "郭和錦":
        st.markdown('<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2>🌸 郭和錦</h2><p style="font-size: 20px;">指導經理加油！</p></div>', unsafe_allow_html=True)
    elif search_q == "大會成功": st.balloons()
    elif df_guest is not None:
        mask = (df_guest['票號_str'].str.contains(search_q, na=False)) | (df_guest['姓名'].str.contains(search_q, na=False))
        found = df_guest[mask]
        if not found.empty:
            row = found.iloc[0]
            t_num = int(row['桌號'])
            st.session_state.focus_table = t_num
            st.markdown(f"""
                <div class="popup-container">
                    <a href="./" target="_self" class="close-x">×</a>
                    <h2>👋 {row['姓名']}</h2>
                    <p style="font-size: 28px; color: red; font-weight: bold; margin: 15px 0;">第 {t_num} 桌</p>
                    <a href="#t_{t_num}" target="_self" style="background:black; color:white; padding:10px 20px; border-radius:10px; text-decoration:none; font-weight:bold;">👉 點我看地圖</a>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("查無資料")

# --- 5. 繪製實景圖或地圖 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv'
if os.path.exists(LAYOUT_FILE):
    try:
        with open(LAYOUT_FILE, mode='r', encoding='utf-8-sig') as f:
            reader = list(csv.reader(f))
            for r_idx, row in enumerate(reader):
                if not any(row): continue
                row_content = "".join(row)
                
                # 繪製舞台、電視牆等標籤 (實景元素)
                if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
                    color = "#FF4B4B" if "舞台" in row_content else ("#333333" if "電視" in row_content else "#2E7D32")
                    st.markdown(f'<div class="label-box-fixed" style="--label-color: {color};">{row_content}</div>', unsafe_allow_html=True)
                    continue
                
                # 繪製桌子按鈕
                cols = st.columns(len(row))
                for c_idx, val in enumerate(row):
                    cell_text = val.strip()
                    if cell_text:
                        with cols[c_idx]:
                            try:
                                t_num = int(float(cell_text))
                                st.markdown(f'<div id="t_{t_num}" class="target-spot"></div>', unsafe_allow_html=True)
                                is_focus = (t_num == st.session_state.get('focus_table', 0))
                                st.button(f"VIP{t_num}" if t_num <= 3 else str(t_num), 
                                          key=f"m_{r_idx}_{c_idx}", 
                                          type="primary" if is_focus else "secondary", 
                                          use_container_width=True)
                            except:
                                st.caption(cell_text)
    except:
        st.error("讀取地圖佈局失敗")