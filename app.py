import streamlit as st
import pandas as pd
import requests
from io import StringIO
import re

# --- 1. 系統設定 ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv&gid=0"

st.set_page_config(page_title="福慧千人宴管理系統", page_icon="🎟️", layout="wide")

if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# --- 🎨 核心 CSS 樣式 ---
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

st.markdown('<div style="text-align: center; color: #d32f2f; font-size: 38px; font-weight: 900; padding-top: 20px;">福慧千人宴 共築聖德願</div>', unsafe_allow_html=True)

# --- 📊 2. 資料載入與清洗 ---
@st.cache_data(ttl=10, show_spinner=False)
def load_data():
    try:
        response = requests.get(SHEET_URL, timeout=10)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            df = pd.read_csv(StringIO(response.text))
            
            # 關鍵修正：解決小數點問題
            # 將所有欄位轉為字串，並把 '.0' 替換掉，再去除空白
            for col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            
            # 桌號轉回整數供地圖按鈕比對
            df['桌號_int'] = pd.to_numeric(df['桌號'], errors='coerce').fillna(0).astype(int)
            return df
    except Exception as e:
        st.error(f"資料載入失敗: {e}")
    return pd.DataFrame(columns=["姓名", "票號", "桌號", "售出者", "備註"])

df_guest = load_data()

# --- 🗺️ 3. 地圖佈局 ---
layout_data = [
    ["", "", "", "舞台", "", "", ""],
    ["", "", "VIP3", "VIP1", "VIP2", "", ""], 
    [""], 
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

tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋", "📝 報到與驗證", "📊 完整名單"])

with tab1:
    search_q = st.text_input("🔍 請輸入「票號」或「貴賓姓名」：", placeholder="例如：296 或 黃蘇霞", key="search_input")
    
    if search_q:
        q = search_q.strip()
        
        # --- 🥚 彩蛋觸發 ---
        if q in ["靜好大仙", "劉來好", "馬慧斌", "郭和錦"]:
            if q in ["靜好大仙", "劉來好"]:
                st.markdown('<div class="popup-container" style="background-color: #FFF9C4;"><a href="./" target="_self" class="close-x">×</a><h2 style="color: #F57F17;">🕯️ 靜好大仙</h2><p style="font-size: 24px; font-weight: bold;">她跟馬經理都在這裡<br>暖心地照看著大家</p></div>', unsafe_allow_html=True)
            elif q == "馬慧斌":
                st.markdown('<div class="popup-container"><a href="./" target="_self" class="close-x">×</a><h2 style="color: #F57F17;">👔 馬慧斌 經理</h2><p style="font-size: 24px; font-weight: bold;">他在現場喔！<br>你有看到嗎？</p></div>', unsafe_allow_html=True)
            elif q == "郭和錦":
                st.markdown('<div class="popup-container" style="background-color: #FCE4EC;"><a href="./" target="_self" class="close-x">×</a><h2 style="color: #EC407A;">🌸 郭和錦</h2><p style="font-size: 26px; font-weight: bold;">賴經理加油！<br>我一直都在這裡陪著妳</p></div>', unsafe_allow_html=True)
        
        # --- 🔍 精確搜尋邏輯 ---
        elif not df_guest.empty:
            # 1. 票號比對：使用正則表達式邊界 \b，確保搜 296 不會中 1296
            # 2. 姓名比對：模糊包含
            mask_ticket = df_guest['票號'].str.contains(rf'\b{re.escape(q)}\b', na=False, regex=True)
            mask_name = df_guest['姓名'].str.contains(q, na=False)
            
            found = df_guest[mask_ticket | mask_name]
            
            if not found.empty:
                row = found.iloc[0]
                table_val = row['桌號_int']
                st.session_state.focus_table = table_val
                
                # 顯示文字處理
                t_label = f"第 {table_val} 桌"
                if "VIP" in row['桌號']: t_label = f"{row['桌號']} 區"

                st.markdown(f"""
                    <div class="popup-container">
                        <a href="./" target="_self" class="close-x">×</a>
                        <h2 style="color: #333;">👋 {row['姓名']} 貴賓</h2>
                        <p style="font-size: 32px; color: #d32f2f; font-weight: bold; margin: 20px 0;">位置：{t_label}</p>
                        <p style="color: #666;">票號：{row['票號']}</p>
                        <a href="#t_{table_val}" target="_self" class="inner-btn">👉 點我看座位</a>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"查無「{q}」的資料。")

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
                    # 錨點處理
                    clean_val = val.replace("VIP", "")
                    st.markdown(f'<div id="t_{clean_val}" class="target-spot"></div>', unsafe_allow_html=True)
                    
                    # 亮燈邏輯
                    is_focus = (st.session_state.focus_table and str(st.session_state.focus_table) == clean_val)
                    st.button(val, key=f"btn_{r_idx}_{c_idx}", type="primary" if is_focus else "secondary", use_container_width=True)

with tab2:
    st.info("系統維護中：報到功能連線正常。")

with tab3:
    st.dataframe(df_guest, use_container_width=True)