import streamlit as st
import pandas as pd
import requests
from io import StringIO

# --- 1. 系統設定 ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴管理系統", page_icon="🎟️", layout="wide")

if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# --- 🎨 核心 CSS (完全保留原樣) ---
st.markdown("""
    <style>
    div.stButton > button:first-child { height: 3em !important; margin-top: 28px !important; }
    .popup-container {
        position: fixed; top: 40%; left: 50%; transform: translate(-50%, -50%);
        width: 380px; background-color: #FFD700; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); z-index: 9999;
        text-align: center; border: 4px solid #DAA520; padding: 40px 20px;
    }
    .close-x {
        position: absolute; top: 15px; right: 20px; font-size: 30px; color: #555; text-decoration: none; font-weight: bold;
    }
    .inner-btn {
        display: inline-block; background-color: #000; color: #fff !important; padding: 15px 30px; border-radius: 12px;
        text-decoration: none; font-size: 18px; font-weight: bold; width: 85%; margin-top: 20px;
    }
    [data-testid="stVerticalBlock"] { gap: 0px !important; }
    [data-testid="stHorizontalBlock"] { margin-bottom: -15px !important; }
    .label-box-fixed {
        background-color: var(--label-color); color: white; text-align: center; padding: 15px !important;
        border-radius: 10px; font-weight: bold; font-size: 22px !important; margin: 15px 0 !important; width: 100%;
    }
    .target-spot { scroll-margin-top: 350px; }
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important; border: 3px solid #FBC02D !important; font-weight: bold; transform: scale(1.1);
    }
    .spacer-row { height: 45px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div style="text-align: center; color: #d32f2f; font-size: 38px; font-weight: 900; padding-top: 20px;">福慧千人宴共築聖德願</div>', unsafe_allow_html=True)

# --- 📊 2. 資料載入 (Google Sheets) ---
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
        return pd.DataFrame(columns=["姓名", "票號", "桌號"])
    except:
        return pd.DataFrame(columns=["姓名", "票號", "桌號"])

df_guest = load_data()

# --- 🗺️ 3. 地圖數據直接嵌入 (不再讀取外部CSV) ---
# 第一排 3桌, 中間 9桌, 電視牆在66-67, 最後兩排 5桌
layout_data = [
    ["", "", "", "舞台", "", "", ""],
    ["", "", "", "1", "2", "3", "", "", ""],
    [""], # 空行
    ["4", "5", "6", "7", "8", "9", "10", "11", "12"],
    ["13", "14", "15", "16", "17", "18", "19", "20", "21"],
    ["22", "23", "24", "25", "26", "27", "28", "29", "30"],
    ["31", "32", "33", "34", "35", "36", "37", "38", "39"],
    ["40", "41", "42", "43", "44", "45", "46", "47", "48"],
    ["49", "50", "51", "52", "53", "54", "55", "56", "57"],
    ["58", "59", "60", "61", "62", "63", "64", "65", "66"],
    ["", "", "", "電視牆", "", "", ""],
    ["67", "68", "69", "70", "71", "72", "73", "74", "75"],
    ["76", "77", "78", "79", "80", "81", "82", "83", "84"],
    ["85", "86", "87", "88", "89", "90", "91", "92", "93"],
    ["94", "95", "96", "97", "98", "99", "100", "101", "102"],
    ["103", "104", "105", "106", "107", "108", "109", "110", "111"],
    ["112", "113", "114", "115", "116", "117", "118", "119", "120"],
    ["", "", "121", "122", "123", "124", "125", "", ""],
    ["", "", "126", "127", "128", "129", "130", "", ""],
    ["", "", "", "入口", "", "", ""]
]

tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋", "📝 批次登記與防呆", "📊 數據中心"])

with tab1:
    search_q = st.text_input("輸入票號或姓名搜尋：", placeholder="例如：1351 或 徐鳳慈", key="search_main")
    
    if search_q:
        # --- 🥚 彩蛋部分 (完全保留) ---
        if search_q in ["靜好大仙", "劉來好"]:
            st.markdown('<div class="popup-container" style="background-color: #FFF9C4;"><a href="./" target="_self" class="close-x">×</a><h2 style="color: #F57F17;">🕯️ 靜好大仙</h2><p style="font-size: 24px; font-weight: bold;">她跟馬經理都在這裡<br>陪著大家</p></div>', unsafe_allow_html=True)
        elif search_q == "陳聰發":
            st.markdown('<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2 style="color: #F57F17;">🕯️ 陳聰發</h2><p style="font-size: 24px; font-weight: bold;">他在旁邊<br>一直幫我們加油喔</p></div>', unsafe_allow_html=True)
        elif search_q == "馬慧斌":
            st.markdown('<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2 style="color: #F57F17;">👔 馬慧斌 經理</h2><p style="font-size: 24px; font-weight: bold;">他在現場喔！</p></div>', unsafe_allow_html=True)
        elif search_q == "郭和錦":
            st.markdown('<div class="popup-container" style="background-color: #FCE4EC;"><a href="./" target="_self" class="close-x">×</a><h2 style="color: #EC407A;">🌸 郭和錦</h2><p style="font-size: 26px; font-weight: bold;">指導經理加油！<br>我一直都在這裡陪著妳</p></div>', unsafe_allow_html=True)
        elif search_q == "大會成功": st.balloons()
        elif not df_guest.empty:
            mask = (df_guest['票號_str'].str.contains(search_q, na=False)) | (df_guest['姓名'].str.contains(search_q, na=False))
            found = df_guest[mask]
            if not found.empty:
                row = found.iloc[0]
                st.session_state.focus_table = int(row['桌號'])
                t_label = f"第 {st.session_state.focus_table} 桌" if st.session_state.focus_table > 3 else f"VIP {st.session_state.focus_table} 桌"
                st.markdown(f"""<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2>👋 {row['姓名']} 貴賓</h2><p style="font-size: 32px; color: #d32f2f; font-weight: bold; margin: 20px 0;">位置：{t_label}</p><a href="#t_{st.session_state.focus_table}" target="_self" class="inner-btn">👉 點我看座位</a></div>""", unsafe_allow_html=True)
            else:
                st.error("❌ 查無資料")

    # --- 🗺️ 地圖渲染 ---
    for r_idx, row in enumerate(layout_data):
        if not any(row):
            st.markdown('<div class="spacer-row"></div>', unsafe_allow_html=True)
            continue
        row_content = "".join(row)
        if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
            color = "#FF4B4B" if "舞台" in row_content else ("#333333" if "電視" in row_content else "#2E7D32")
            st.markdown(f'<div class="label-box-fixed" style="--label-color: {color};">{row_content}</div>', unsafe_allow_html=True)
            continue
        
        cols = st.columns(len(row))
        for c_idx, val in enumerate(row):
            with cols[c_idx]:
                if val.strip():
                    try:
                        t_num = int(val)
                        st.markdown(f'<div id="t_{t_num}" class="target-spot"></div>', unsafe_allow_html=True)
                        is_focus = (t_num == st.session_state.focus_table)
                        st.button(f"VIP{t_num}" if t_num <= 3 else str(t_num), key=f"m_{r_idx}_{c_idx}", type="primary" if is_focus else "secondary", use_container_width=True)
                    except:
                        st.caption(val)

with tab2:
    st.subheader("📝 登記與驗證功能")
    st.info("此功能目前為介面展示")

with tab3:
    st.dataframe(df_guest, use_container_width=True)