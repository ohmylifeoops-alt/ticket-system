import streamlit as st
import pandas as pd
import requests
from io import StringIO
import os
import csv

# --- 1. 頁面基本設定 ---
st.set_page_config(page_title="福慧千人宴共築聖德願", page_icon="🎟️", layout="wide")

# 初始化 session_state
if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# --- 🎨 核心 CSS (精緻化實景與彈窗) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main-header {
        text-align: center; color: #d32f2f !important; font-size: 38px !important;
        font-weight: 900 !important; margin-bottom: 5px !important; padding-top: 25px !important;
    }
    .sub-header {
        text-align: center; color: #555 !important; font-size: 18px !important; margin-bottom: 20px !important;
    }
    /* 彈窗樣式 - 增加寬度以容納長感言 */
    .popup-container {
        position: fixed; top: 45%; left: 50%; transform: translate(-50%, -50%);
        width: 400px; background-color: #FFD700; border-radius: 25px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.6); z-index: 10000;
        text-align: center; border: 4px solid #DAA520; padding: 35px 25px;
    }
    .close-x { position: absolute; top: 10px; right: 20px; font-size: 30px; font-weight: bold; color: #333; text-decoration: none; }
    
    /* 實景標籤樣式 */
    .label-box-fixed {
        background-color: var(--label-color); color: white; text-align: center; padding: 12px !important;
        border-radius: 10px; font-weight: bold; font-size: 22px !important; margin: 15px 0 !important; width: 100%;
    }
    
    /* 地圖按鈕樣式 */
    [data-testid="stHorizontalBlock"] { margin-bottom: -20px !important; }
    .stButton > button { height: 2.8em !important; font-size: 16px !important; }
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important; border: 3px solid #FBC02D !important; font-weight: bold;
    }
    .target-spot { scroll-margin-top: 60px; }
    </style>
    """, unsafe_allow_html=True)

# --- 📖 顯示標頭 ---
st.markdown('<div class="main-header">福慧千人宴共築聖德願</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">桌次查詢系統 (線上/線下/管理整合版)</div>', unsafe_allow_html=True)

# --- 🛠️ 側邊欄：檔案管理與上傳功能 ---
with st.sidebar:
    st.header("⚙️ 系統後台")
    uploaded_guest = st.file_uploader("上傳最新賓客總表 (CSV)", type="csv")
    if uploaded_guest:
        with open("賓客總表.csv", "wb") as f:
            f.write(uploaded_guest.getbuffer())
        st.success("✅ 賓客名單已更新！")
        
    uploaded_layout = st.file_uploader("上傳最新排桌地圖 (CSV)", type="csv")
    if uploaded_layout:
        with open("排桌.xlsx - 工作表1.csv", "wb") as f:
            f.write(uploaded_layout.getbuffer())
        st.success("✅ 地圖佈局已更新！")

# --- 🔍 3. 搜尋框 ---
search_q = st.text_input("", placeholder="🔍 輸入姓名或票號直接搜尋...", key="search_main", label_visibility="collapsed")

# --- 📊 4. 資料載入邏輯 (雲端優先，本地備援) ---
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
        df = pd.read_csv('賓客總表.csv')
        df['票號_str'] = df['票號'].astype(str)
        df['桌號'] = pd.to_numeric(df['桌號'], errors='coerce').fillna(0).astype(int)
        return df
    return None

df_guest = load_data()

# --- 🎭 5. 搜尋邏輯與「所有感人彩蛋」全部找回 ---
if search_q:
    # 🌸 彩蛋 1: 郭和錦先生 (指導經理的亡夫)
    if "郭和錦" in search_q:
        st.markdown('<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2 style="color:#d32f2f;">🌸 郭和錦</h2><p style="font-size: 22px; font-weight:bold;">指導經理加油！<br>我一直都在這裡陪著妳<br>看著大家共築聖德願</p></div>', unsafe_allow_html=True)
    
    # 🕯️ 彩蛋 2: 馬慧斌經理 (馬經理)
    elif "馬慧斌" in search_q or search_q == "馬經理":
        st.markdown('<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2 style="color:#2E7D32;">👔 馬慧斌 經理</h2><p style="font-size: 20px; font-weight:bold;">他也在這兒呢！<br>正熱情地張羅著大家<br>讓每個人都感受到溫暖</p></div>', unsafe_allow_html=True)
        
    # 🌟 彩蛋 3: 陳聰發先生
    elif "陳聰發" in search_q:
        st.markdown('<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2 style="color:#1565C0;">🌟 陳聰發</h2><p style="font-size: 20px; font-weight:bold;">他正在微笑著點頭<br>守護著這場盛會的圓滿<br>大家辛苦了！</p></div>', unsafe_allow_html=True)

    # 🏮 彩蛋 4: 靜好大仙 (劉來好)
    elif search_q in ["靜好大仙", "劉來好"]:
        st.markdown('<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2 style="color:#F57F17;">🕯️ 靜好大仙</h2><p style="font-size: 20px; font-weight:bold;">她與馬經理都在這裡<br>暖心地照看著每位家人</p></div>', unsafe_allow_html=True)
    
    # ✨ 成功與辛苦彩蛋
    elif search_q == "大會成功": st.balloons()
    elif search_q == "辛苦了": st.snow()
    
    # 🔍 正常查詢
    elif df_guest is not None:
        mask = (df_guest['票號_str'].str.contains(search_q, na=False)) | (df_guest['姓名'].str.contains(search_q, na=False))
        found = df_guest[mask]
        if not found.empty:
            row = found.iloc[0]
            st.session_state.focus_table = int(row['桌號'])
            st.markdown(f"""
                <div class="popup-container">
                    <a href="./" target="_self" class="close-x">×</a>
                    <h2 style="color:black;">👋 {row['姓名']} 貴賓</h2>
                    <p style="font-size: 32px; color: #d32f2f; font-weight: bold; margin: 20px 0;">位置：第 {st.session_state.focus_table} 桌</p>
                    <a href="#t_{st.session_state.focus_table}" target="_self" style="display:inline-block; background:black; color:white; padding:12px 25px; border-radius:10px; text-decoration:none; font-weight:bold; font-size:18px;">👉 點我看地圖</a>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ 查無資料，請確認輸入是否正確。")

# --- 🗺️ 6. 繪製實景圖與地圖 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv'
if os.path.exists(LAYOUT_FILE):
    try:
        with open(LAYOUT_FILE, mode='r', encoding='utf-8-sig') as f:
            reader = list(csv.reader(f))
            for r_idx, row in enumerate(reader):
                if not any(row):
                    st.markdown('<div style="height:40px;"></div>', unsafe_allow_html=True)
                    continue
                row_content = "".join(row)
                
                # 實景元素
                if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
                    color = "#FF4B4B" if "舞台" in row_content else ("#333333" if "電視" in row_content else "#2E7D32")
                    st.markdown(f'<div class="label-box-fixed" style="--label-color: {color};">{row_content}</div>', unsafe_allow_html=True)
                    continue
                
                # 地圖桌次
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
    except Exception as e:
        st.error(f"地圖讀取失敗：{e}")