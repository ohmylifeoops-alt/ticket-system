import streamlit as st
import pandas as pd
import requests
from io import StringIO
import os
import csv

# --- 1. 頁面基本設定 ---
st.set_page_config(page_title="福慧千人宴共築聖德願", page_icon="🎟️", layout="wide")

# --- 🎨 核心 CSS (完全恢復你最滿意的視覺) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main-header {
        text-align: center; color: #d32f2f !important; font-size: 38px !important;
        font-weight: 900 !important; margin-bottom: 5px !important; padding-top: 20px !important;
    }
    /* 彈窗樣式 */
    .popup-container {
        position: fixed; top: 45%; left: 50%; transform: translate(-50%, -50%);
        width: 380px; background-color: #FFD700; border-radius: 25px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.6); z-index: 10000;
        text-align: center; border: 4px solid #DAA520; padding: 30px 20px;
    }
    .close-x { position: absolute; top: 10px; right: 20px; font-size: 30px; font-weight: bold; color: #333; text-decoration: none; }
    
    /* 實景標籤 */
    .label-box-fixed {
        background-color: var(--label-color); color: white; text-align: center; padding: 12px !important;
        border-radius: 10px; font-weight: bold; font-size: 22px !important; margin: 15px 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 📖 顯示標頭 ---
st.markdown('<div class="main-header">福慧千人宴共築聖德願</div>', unsafe_allow_html=True)

# --- 📊 2. 資料載入 (雲端修復版) ---
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"
    try:
        response = requests.get(sheet_url, timeout=5)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            df['票號_str'] = df['票號'].astype(str)
            df['桌號'] = pd.to_numeric(df['桌號'], errors='coerce').fillna(0).astype(int)
            return df
    except:
        pass
    if os.path.exists('賓客總表.csv'):
        return pd.read_csv('賓客總表.csv')
    return None

df_guest = load_data()

# --- 📑 3. 建立三個分頁 (Tabs) ---
tab1, tab2, tab3 = st.tabs(["🔍 桌次查詢", "🗺️ 場地地圖", "⚙️ 後台管理"])

# --- Tab 1: 桌次查詢 ---
with tab1:
    search_q = st.text_input("🔍 輸入姓名或票號：", placeholder="例如：張小明 或 1234", key="search_main")
    
    if search_q:
        # 所有感人彩蛋
        if "郭和錦" in search_q:
            st.markdown('<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2 style="color:#d32f2f;">🌸 郭和錦</h2><p style="font-size: 22px; font-weight:bold;">指導經理加油！<br>我一直都在這裡陪著妳</p></div>', unsafe_allow_html=True)
        elif "馬慧斌" in search_q or search_q == "馬經理":
            st.markdown('<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2 style="color:#2E7D32;">👔 馬慧斌 經理</h2><p style="font-size: 20px; font-weight:bold;">他也在這兒呢！<br>正熱情地張羅著大家</p></div>', unsafe_allow_html=True)
        elif "陳聰發" in search_q:
            st.markdown('<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2 style="color:#1565C0;">🌟 陳聰發</h2><p style="font-size: 20px; font-weight:bold;">他正在微笑著點頭<br>大家辛苦了！</p></div>', unsafe_allow_html=True)
        elif search_q in ["靜好大仙", "劉來好"]:
            st.markdown('<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2 style="color:#F57F17;">🕯️ 靜好大仙</h2><p style="font-size: 20px; font-weight:bold;">她與馬經理都在這裡<br>暖心地照看著每位家人</p></div>', unsafe_allow_html=True)
        elif search_q == "大會成功": st.balloons()
        
        # 正常查詢
        elif df_guest is not None:
            mask = (df_guest['票號_str'].str.contains(search_q, na=False)) | (df_guest['姓名'].str.contains(search_q, na=False))
            found = df_guest[mask]
            if not found.empty:
                row = found.iloc[0]
                t_num = int(row['桌號'])
                st.markdown(f'<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2>👋 {row["姓名"]} 貴賓</h2><p style="font-size: 32px; color: #d32f2f; font-weight: bold;">第 {t_num} 桌</p></div>', unsafe_allow_html=True)
            else:
                st.error("查無資料")

# --- Tab 2: 場地地圖 ---
with tab2:
    LAYOUT_FILE = '排桌.xlsx - 工作表1.csv'
    if os.path.exists(LAYOUT_FILE):
        with open(LAYOUT_FILE, mode='r', encoding='utf-8-sig') as f:
            reader = list(csv.reader(f))
            for r_idx, row in enumerate(reader):
                if not any(row):
                    st.write("")
                    continue
                row_content = "".join(row)
                if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
                    color = "#FF4B4B" if "舞台" in row_content else ("#333333" if "電視" in row_content else "#2E7D32")
                    st.markdown(f'<div class="label-box-fixed" style="--label-color: {color};">{row_content}</div>', unsafe_allow_html=True)
                    continue
                cols = st.columns(len(row))
                for c_idx, val in enumerate(row):
                    cell_text = val.strip()
                    if cell_text:
                        with cols[c_idx]:
                            try:
                                t_num = int(float(cell_text))
                                st.button(f"VIP{t_num}" if t_num <= 3 else str(t_num), key=f"map_{r_idx}_{c_idx}", use_container_width=True)
                            except:
                                st.caption(cell_text)

# --- Tab 3: 後台管理 ---
with tab3:
    st.subheader("📥 檔案更新")
    up_guest = st.file_uploader("更新賓客名單 (CSV)", type="csv")
    if up_guest:
        with open("賓客總表.csv", "wb") as f:
            f.write(up_guest.getbuffer())
        st.success("賓客名單更新成功！")
        
    up_map = st.file_uploader("更新地圖佈局 (CSV)", type="csv")
    if up_map:
        with open("排桌.xlsx - 工作表1.csv", "wb") as f:
            f.write(up_map.getbuffer())
        st.success("地圖佈局更新成功！")