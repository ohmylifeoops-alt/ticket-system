import streamlit as st
import pandas as pd
import os
import requests
from io import StringIO
import csv

# --- 1. 系統設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="福慧千人宴管理系統", page_icon="🎟️", layout="wide")

if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# --- 🎨 核心 CSS (恢復最滿意的視覺) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main-header {
        text-align: center; color: #d32f2f !important; font-size: 38px !important;
        font-weight: 900 !important; margin-bottom: 5px !important; padding-top: 25px !important;
    }
    .popup-container {
        position: fixed; top: 45%; left: 50%; transform: translate(-50%, -50%);
        width: 400px; background-color: #FFD700; border-radius: 25px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.6); z-index: 10000;
        text-align: center; border: 4px solid #DAA520; padding: 35px 25px;
    }
    .close-x { position: absolute; top: 10px; right: 20px; font-size: 30px; font-weight: bold; color: #333; text-decoration: none; }
    .inner-btn {
        display: inline-block; background-color: #000; color: #fff !important; padding: 15px 30px; border-radius: 12px;
        text-decoration: none; font-size: 18px; font-weight: bold; width: 85%; margin-top: 20px;
    }
    .label-box-fixed {
        background-color: var(--label-color); color: white; text-align: center; padding: 15px !important;
        border-radius: 10px; font-weight: bold; font-size: 22px !important; margin: 15px 0 !important; width: 100%;
    }
    [data-testid="stHorizontalBlock"] { margin-bottom: -15px !important; }
    .stButton > button { height: 3em !important; font-size: 16px !important; }
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important; border: 3px solid #FBC02D !important; 
        font-weight: bold; transform: scale(1.05);
    }
    .target-spot { scroll-margin-top: 350px; }
    .spacer-row { height: 45px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header">福慧千人宴共築聖德願</div>', unsafe_allow_html=True)

# --- 📊 2. 資料載入 (雲端優化版) ---
@st.cache_data(ttl=30, show_spinner=False)
def load_data():
    try:
        response = requests.get(SHEET_URL, timeout=10)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            data = pd.read_csv(StringIO(response.text))
            if '票號' in data.columns: data['票號_str'] = data['票號'].astype(str)
            if '桌號' in data.columns: data['桌號'] = pd.to_numeric(data['桌號'], errors='coerce').fillna(0).astype(int)
            return data
    except:
        if os.path.exists('賓客總表.csv'):
            return pd.read_csv('賓客總表.csv')
    return pd.DataFrame(columns=["姓名", "票號", "桌號"])

df_guest = load_data()

# --- 📑 3. 三分頁佈局 ---
tab1, tab2, tab3 = st.tabs(["🔍 桌次搜尋", "🗺️ 場地地圖", "⚙️ 後台管理"])

with tab1:
    search_q = st.text_input("🔍 輸入姓名或票號：", placeholder="例如：張小明 或 1234", key="search_main")
    if search_q:
        if "郭和錦" in search_q:
            st.markdown('<div class="popup-container" style="background-color: #FCE4EC;"><a href="./" target="_self" class="close-x">×</a><h2 style="color: #EC407A;">🌸 郭和錦</h2><p style="font-size: 26px; font-weight: bold; color: #880E4F;">賴經理加油！<br>我一直都在這裡陪著妳</p></div>', unsafe_allow_html=True)
        elif search_q == "陳聰發":
            st.markdown('<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2 style="color: #F57F17;">🕯️ 陳聰發</h2><p style="font-size: 24px; font-weight: bold;">他在旁邊<br>一直幫我們加油喔</p></div>', unsafe_allow_html=True)
        elif search_q == "馬慧斌":
            st.markdown('<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2 style="color: #F57F17;">👔 馬慧斌 經理</h2><p style="font-size: 24px; font-weight: bold;">他在現場喔！<br>你有看到嗎？</p></div>', unsafe_allow_html=True)
        elif search_q in ["靜好大仙", "劉來好"]:
            st.markdown('<div class="popup-container" style="background-color: #FFF9C4;"><a href="./" target="_self" class="close-x">×</a><h2 style="color: #F57F17;">🕯️ 靜好大仙</h2><p style="font-size: 24px; font-weight: bold; color: #424242;">她跟馬經理都在這裡<br>陪著大家</p></div>', unsafe_allow_html=True)
        elif search_q == "大會成功": st.balloons()
        elif not df_guest.empty:
            mask = (df_guest['票號_str'].str.contains(search_q, na=False)) | (df_guest['姓名'].str.contains(search_q, na=False))
            found = df_guest[mask]
            if not found.empty:
                row = found.iloc[0]
                st.session_state.focus_table = int(row['桌號'])
                t_label = f"第 {st.session_state.focus_table} 桌" if st.session_state.focus_table > 3 else f"VIP {st.session_state.focus_table} 桌"
                st.markdown(f"""<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2 style="color: black;">👋 {row['姓名']} 貴賓</h2><p style="font-size: 32px; color: #d32f2f; font-weight: bold; margin: 20px 0;">位置：{t_label}</p><a href="#t_{st.session_state.focus_table}" target="_self" class="inner-btn">👉 點我看座位</a></div>""", unsafe_allow_html=True)
            else:
                st.error("❌ 查無資料")

with tab2:
    if os.path.exists(LAYOUT_FILE):
        try:
            # 【關鍵修復】加入 on_bad_lines='skip' 防止 CSV 格式不齊導致崩潰
            df_map = pd.read_csv(LAYOUT_FILE, header=None, skip_blank_lines=False, on_bad_lines='skip', engine='python')
            num_cols = len(df_map.columns)
            for r_idx, row in df_map.iterrows():
                if row.isnull().all() or "".join([str(v) for v in row if not pd.isna(v)]).strip() == "":
                    st.markdown('<div class="spacer-row"></div>', unsafe_allow_html=True)
                    continue
                row_content = "".join([str(v) for v in row if not pd.isna(v)])
                if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
                    color = "#FF4B4B" if "舞台" in row_content else ("#333333" if "電視" in row_content else "#2E7D32")
                    st.markdown(f'<div class="label-box-fixed" style="--label-color: {color};">{row_content}</div>', unsafe_allow_html=True)
                    continue
                cols = st.columns(num_cols)
                for c_idx, val in enumerate(row):
                    with cols[c_idx]:
                        cell_text = str(val).strip() if not pd.isna(val) else ""
                        if cell_text not in ["", "nan"]:
                            try:
                                t_num = int(float(val))
                                st.markdown(f'<div id="t_{t_num}" class="target-spot"></div>', unsafe_allow_html=True)
                                is_focus = (t_num == st.session_state.focus_table)
                                st.button(f"VIP{t_num}" if t_num <= 3 else str(t_num), key=f"m_{r_idx}_{c_idx}", type="primary" if is_focus else "secondary", use_container_width=True)
                            except:
                                st.caption(cell_text)
        except Exception as e:
            st.error(f"地圖檔案格式錯誤：{e}")

with tab3:
    st.subheader("⚙️ 線上後台管理")
    up_guest = st.file_uploader("手動更新賓客名單 (CSV)", type="csv")
    if up_guest:
        with open("賓客總表.csv", "wb") as f: f.write(up_guest.getbuffer())
        st.success("✅ 名單已更新！")
    up_map = st.file_uploader("手動更新地圖佈局 (CSV)", type="csv")
    if up_map:
        with open(LAYOUT_FILE, "wb") as f: f.write(up_map.getbuffer())
        st.success("✅ 地圖已更新！")