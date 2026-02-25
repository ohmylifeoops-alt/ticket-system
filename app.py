import streamlit as st
import pandas as pd
import os
import io

# --- 1. 系統設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴桌次實景管理系統", page_icon="🎟️", layout="wide")

if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# --- 🎨 核心 CSS 修正：左右拉開、上下壓縮 ---
st.markdown("""
    <style>
    /* 1. 搜尋區域對齊 */
    div.stButton > button:first-child {
        height: 3em !important;
        margin-top: 28px !important;
    }

    /* 2. 浮動視窗絕對排版 */
    .popup-container {
        position: fixed; top: 35%; left: 50%; transform: translate(-50%, -50%);
        width: 380px; background-color: #FFD700; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); z-index: 9999;
        text-align: center; border: 4px solid #DAA520; 
        padding: 45px 20px 30px 20px; animation: fadeIn 0.3s forwards;
    }
    
    .close-x {
        position: absolute; top: 10px; right: 20px;
        font-size: 35px; color: #555; text-decoration: none;
        font-family: Arial, sans-serif; font-weight: bold; line-height: 1;
    }

    .anchor-btn {
        display: inline-block; background-color: #000; color: #fff !important;
        padding: 15px 30px; border-radius: 10px; text-decoration: none;
        font-size: 18px; font-weight: bold; width: 85%; margin-top: 15px;
    }

    /* 3. 地圖間距優化核心 */
    [data-testid="stHorizontalBlock"] {
        gap: 0.5rem !important; /* 👈 關鍵：把左右間距調回來，原本是 0px */
    }
    [data-testid="column"] {
        margin-bottom: -22px !important; /* 👈 關鍵：繼續保持上下極致壓縮 */
    }
    
    /* 桌子按鈕微調 */
    .stButton > button {
        height: 35px !important;
        padding: 0px !important;
        font-size: 14px !important;
    }
    
    .label-box {
        margin: 10px 0 !important;
        padding: 10px !important;
        font-size: 18px;
    }

    .table-anchor { scroll-margin-top: 350px; }
    
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important;
        border: 3px solid #FBC02D !important; font-weight: bold;
        transform: scale(1.1);
    }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=30, show_spinner=False)
def load_data():
    try:
        data = pd.read_csv(SHEET_URL)
        if "桌號" in data.columns:
            data['桌號'] = pd.to_numeric(data['桌號'], errors='coerce').fillna(0).astype(int)
        if "票號" in data.columns:
            data['票號'] = pd.to_numeric(data['票號'], errors='coerce').fillna(0).astype(int)
        return data
    except:
        return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

df_guest = load_data()

def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error(f"❌ 找不到佈局檔案：{LAYOUT_FILE}")
        return

    df_map = pd.read_csv(LAYOUT_FILE, header=None)
    num_cols = len(df_map.columns) 
    highlight_set = set(highlighted_tables)
    
    st.markdown("### 🏟️ 千人宴場地實景佈局圖")
    
    for r_idx, row in df_map.iterrows():
        row_content = "".join([str(v) for v in row if not pd.isna(v)])
        if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
            color = "#FF4B4B" if "舞台" in row_content else "#2E7D32"
            st.markdown(f"<div class='label-box' style='background-color:{color}; color:white; text-align:center; border-radius:10px; font-weight:bold;'>{row_content}</div>", unsafe_allow_html=True)
            continue

        cols = st.columns(num_cols) 
        for c_idx, val in enumerate(row):
            with cols[c_idx]:
                cell_text = str(val).strip() if not pd.isna(val) else ""
                if cell_text not in ["", "nan"]:
                    try:
                        table_num = int(float(val))
                        is_active = table_num in highlight_set
                        display_name = f"VIP{table_num}" if table_num in [1,2,3] else str(table_num)
                        st.markdown(f"<div id='table_{table_num}' class='table-anchor'></div>", unsafe_allow_html=True)
                        st.button(display_name, key=f"btn_{r_idx}_{c_idx}_{table_num}", type="primary" if is_active else "secondary", use_container_width=True)
                    except:
                        st.markdown(f"<p style='font-size:10px; text-align:center; margin:0; color:#666;'>{cell_text}</p>", unsafe_allow_html=True)

st.title("🎟️ 千人宴桌次實景管理系統")
tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋", "📝 批次登記與防呆", "📊 數據中心"])

with tab1:
    c_input, c_btn = st.columns([4, 1])
    with c_input:
        search_q = st.text_input("請輸入票號查詢：", placeholder="請輸入票號數字，例如：1351", key="search_main")
    with c_btn:
        search_trigger = st.button("🔍 查詢")

    if search_q or search_trigger:
        try:
            q_num = int(search_q)
            found = df_guest[df_guest['票號'] == q_num]
            if not found.empty:
                first_row = found.iloc[0]
                st.session_state.focus_table = int(first_row['桌號'])
                st.markdown(f"""
                    <div class="popup-container">
                        <a href="./" target="_self" class="close-x">×</a>
                        <h2 style="color: black; margin: 0;">👋 {first_row['姓名']} 貴賓</h2>
                        <p style="font-size: 28px; color: #d32f2f; font-weight: bold; margin: 20px 0;">您的位置在：第 {st.session_state.focus_table if st.session_state.focus_table > 3 else 'VIP' + str(st.session_state.focus_table)} 桌</p>
                        <a href="#table_{st.session_state.focus_table}" target="_self" class="anchor-btn">👉 點我看座位 (自動定位)</a>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.session_state.focus_table = None
                if search_q: st.error("查與此票號不符")
        except:
            if search_q: st.error("請輸入數字")

    draw_seating_chart([st.session_state.focus_table] if st.session_state.focus_table else [])

# Tab2 & Tab3 代碼與之前完全一致，維持登記功能...
# (此處省略 Tab2, Tab3 重複內容以保持回應簡潔)